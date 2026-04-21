#!/usr/bin/env bash
# =============================================================================
# MiniGamer 服务器端一键部署脚本
# =============================================================================
# 用法（在服务器上以 ubuntu 用户身份执行）：
#   bash ~/apps/minigamer/deploy/server-setup.sh
#
# 本脚本是 **幂等** 的，重复执行安全：
#   - Docker 已装就跳过
#   - 镜像加速已配就跳过
#   - 容器已在跑就重新 up（不会丢数据，因为有 named volumes）
# =============================================================================

set -euo pipefail

APP_DIR="$HOME/apps/minigamer"
DEPLOY_DIR="$APP_DIR/deploy"

log() { echo -e "\033[36m[$(date +%H:%M:%S)]\033[0m $*"; }
warn() { echo -e "\033[33m[WARN]\033[0m $*"; }
die()  { echo -e "\033[31m[ERROR]\033[0m $*" >&2; exit 1; }

# ---------- 0. 基础校验 ----------
[[ -d "$APP_DIR" ]]    || die "工程目录不存在：$APP_DIR（请先上传代码）"
[[ -f "$DEPLOY_DIR/.env" ]] || die "$DEPLOY_DIR/.env 不存在，请先从本地带过来"
[[ -f "$DEPLOY_DIR/docker-compose.yml" ]] || die "docker-compose.yml 不存在"

log "工程目录：$APP_DIR"

# ---------- 1. 安装 Docker（如未安装） ----------
if command -v docker >/dev/null 2>&1; then
    log "Docker 已安装：$(docker --version)"
else
    log "Docker 未安装，开始安装..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo bash /tmp/get-docker.sh
    sudo usermod -aG docker "$USER"
    log "Docker 安装完成（用户组变更需下次登录后生效）"
fi

# ---------- 2. 配置腾讯云镜像加速（幂等） ----------
MIRROR_JSON='{"registry-mirrors":["https://mirror.ccs.tencentyun.com"]}'
if [[ -f /etc/docker/daemon.json ]] && grep -q "mirror.ccs.tencentyun.com" /etc/docker/daemon.json; then
    log "Docker 镜像加速已配置"
else
    log "配置 Docker 镜像加速..."
    sudo mkdir -p /etc/docker
    # printf 避免 CRLF 污染
    printf '%s\n' "$MIRROR_JSON" | sudo tee /etc/docker/daemon.json >/dev/null
    sudo systemctl reset-failed docker || true
    sudo systemctl restart docker
    sleep 2
fi

# ---------- 3. 确认 Docker service 活着 ----------
if ! sudo systemctl is-active --quiet docker; then
    die "Docker 服务未运行，请 sudo journalctl -xeu docker 查看原因"
fi
log "Docker service: active"

# ---------- 4. 预检 .env 关键项 ----------
cd "$DEPLOY_DIR"
check_env() {
    local key="$1"
    local val
    val="$(grep -E "^${key}=" .env | head -1 | cut -d= -f2-)"
    if [[ -z "$val" || "$val" == *REPLACE_ME* || "$val" == *CHANGE_ME* ]]; then
        die ".env 的 $key 未填写或仍是占位符（当前值=$val）"
    fi
}
check_env JWT_SECRET_KEY
check_env WECHAT_APPID
check_env POSTGRES_PASSWORD
# Qwen 可以不填（会回退到 mock），只给 warning
if grep -qE '^QWEN_API_KEY=\s*$|^QWEN_API_KEY=.*REPLACE' .env; then
    warn "QWEN_API_KEY 未配置，AI 对话将回退到 mock"
fi
log ".env 关键项校验通过"

# ---------- 5. 启动容器 ----------
log "启动 docker compose（首次会拉镜像 + 构建 app，可能 2-5 分钟）..."
sudo docker compose pull postgres redis nginx 2>&1 | tail -5 || true
sudo docker compose up -d --build

# ---------- 6. 等待 app 健康 ----------
log "等待服务就绪..."
for i in {1..30}; do
    if sudo docker compose ps --format json 2>/dev/null | grep -q '"State":"running"'; then
        # 再额外 ping 一下 nginx
        if curl -fsS http://127.0.0.1/health >/dev/null 2>&1; then
            log "✅ 服务已就绪"
            break
        fi
    fi
    sleep 2
    [[ $i -eq 30 ]] && warn "60 秒内未看到健康响应，请手动检查"
done

# ---------- 7. 输出状态 ----------
echo
echo "====================== 容器状态 ======================"
sudo docker compose ps
echo
echo "====================== 自检 ======================"
echo -n "  GET http://127.0.0.1/health -> "
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1/health || true
echo -n "  GET http://127.0.0.1/       -> "
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1/ || true
echo -n "  GET http://127.0.0.1/api/v1/ (docs via app) -> "
# docs 走 nginx /api/ 代理不到，直接访问 app 容器内部 8000
sudo docker compose exec -T app curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/docs 2>/dev/null || echo "skip"
echo
echo "====================== 下一步 ======================"
echo "  1. 在腾讯云轻量控制台 -> 防火墙，放行 TCP:80 给 0.0.0.0/0"
echo "  2. 本地浏览器打开：http://81.71.89.228/health"
echo "     期望看到 {\"status\":\"healthy\"}"
echo "  3. 微信开发者工具：详情 -> 本地设置 -> 勾选「不校验合法域名」-> 清缓存 -> 重编译"
echo "  4. 日志：sudo docker compose logs -f app"
echo "  5. 停止：sudo docker compose down"
echo
