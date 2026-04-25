#!/usr/bin/env bash
# MiniGamer 内网 CVM 部署脚本
# 在 CVM 上执行：bash /tmp/deploy-internal.sh
set -euo pipefail

APP_DIR=/data/minigamer/app
ENV_FILE=/data/minigamer/.env
# 使用前用 sed 把 PAT_PLACEHOLDER 替换成真实 PAT，不要把真实值提交到 Git
REPO_URL='https://66503839-crypto:PAT_PLACEHOLDER@github.com/66503839-crypto/Walter-Project.git'

log() { echo -e "\033[36m[$(date +%H:%M:%S)]\033[0m $*"; }

# ---------- 1. 准备数据目录 ----------
log "创建 /data/minigamer 子目录..."
mkdir -p /data/minigamer/pg-data /data/minigamer/redis-data /data/logs/minigamer

# ---------- 2. Clone 或更新代码 ----------
if [[ -d "$APP_DIR/.git" ]]; then
    log "代码仓库已存在，pull 最新..."
    cd "$APP_DIR"
    git fetch origin main --quiet
    git reset --hard origin/main
else
    log "首次 clone 代码..."
    git clone --depth=1 "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
    # clone 完后立刻把 remote 的 PAT 去掉
    git remote set-url origin https://github.com/66503839-crypto/Walter-Project.git
fi

log "当前代码版本：$(git log -1 --oneline)"

# ---------- 3. 生成 .env（如果不存在） ----------
if [[ ! -f "$ENV_FILE" ]]; then
    log "生成 /data/minigamer/.env（从模板复制，敏感值已填占位）..."
    JWT_KEY=$(openssl rand -hex 32)
    DB_PWD=$(openssl rand -base64 24 | tr -d '=+/' | head -c 32)
    cat > "$ENV_FILE" << EOF
APP_ENV=prod
APP_NAME=MiniGamer-Internal
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

POSTGRES_USER=minigamer
POSTGRES_PASSWORD=${DB_PWD}
POSTGRES_DB=minigamer
DATABASE_URL=postgresql+asyncpg://minigamer:${DB_PWD}@postgres:5432/minigamer

REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=${JWT_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TTL_MINUTES=60
JWT_REFRESH_TTL_DAYS=30

WECHAT_APPID=wxba83d0ebfc02609e
WECHAT_SECRET=REPLACE_ME_WITH_WECHAT_SECRET
WECHAT_API_BASE=https://api.weixin.qq.com

AI_PROVIDER=tokenplan
AI_DEFAULT_MODEL=tc-code-latest

TOKENPLAN_API_KEY=REPLACE_ME_WITH_TOKENPLAN_KEY
TOKENPLAN_BASE_URL=https://api.lkeap.cloud.tencent.com/plan/v3
TOKENPLAN_DEFAULT_MODEL=tc-code-latest

DEEPSEEK_API_KEY=REPLACE_ME_WITH_DEEPSEEK_KEY_OR_LEAVE_EMPTY
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1

CORS_ORIGINS=https://servicewechat.com,https://walteryang-any3.devcloud.woa.com

LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
EOF
    chmod 600 "$ENV_FILE"
    log "✅ .env 已生成。请编辑以下 3 个 REPLACE_ME："
    log "   - WECHAT_SECRET"
    log "   - TOKENPLAN_API_KEY"
    log "   - DEEPSEEK_API_KEY（可选，不用就保持占位或置空）"
    log "   编辑完后再跑 docker compose up"
    log ""
    log "   nano $ENV_FILE"
    exit 0
else
    log "✅ .env 已存在，跳过生成"
fi

# ---------- 4. 检查 .env 没有遗留 REPLACE_ME ----------
if grep -q "REPLACE_ME_WITH_WECHAT\|REPLACE_ME_WITH_TOKENPLAN" "$ENV_FILE"; then
    log "❌ .env 里还有 REPLACE_ME 占位，请编辑后再跑"
    grep "REPLACE_ME" "$ENV_FILE" || true
    exit 1
fi

# ---------- 5. 启动 ----------
cd "$APP_DIR/deploy"
log "docker compose up..."
docker compose --env-file "$ENV_FILE" -f docker-compose.internal.yml up -d --build

log "等待健康检查（30 秒）..."
for i in $(seq 1 15); do
    if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
        log "✅ app 容器健康"
        break
    fi
    sleep 2
done

echo
echo "====================== 容器状态 ======================"
docker compose -f docker-compose.internal.yml ps
echo
echo "====================== 自检 ======================"
echo -n "  local 8000/health -> "
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/health
echo -n "  nginx /mg-api/health -> "
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1/mg-api/health
echo -n "  docs -> "
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/docs
echo
echo "外部访问：https://walteryang-any3.devcloud.woa.com/mg-api/health"
