# MiniGamer 部署手册

> 目标服务器：腾讯云轻量应用服务器  
> 公网 IP：`81.71.89.228`（广州七区）  
> 内网 IP：`10.1.0.11`  
> 系统：Ubuntu Server 24.04 LTS  
> 规格：2核 4GB / 60GB SSD / 200Mbps  
> 预装镜像：OpenClaw(龙虾)

---

## 一、服务器首次准备（只做一次）

### 1.1 登录服务器

**前提**：先在腾讯云控制台「服务器登录 → 重置密码 或 绑定密钥」，然后：

```bash
# Windows PowerShell / WSL / macOS Terminal
ssh ubuntu@81.71.89.228
```

初始登录名是 `ubuntu`（Ubuntu 镜像约定）。

### 1.2 基础安全加固

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 创建部署专用用户（可选，也可以继续用 ubuntu）
# sudo adduser deploy
# sudo usermod -aG sudo deploy

# 配置防火墙（腾讯云轻量还要去控制台「防火墙」放行）
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 关闭密码登录、只允许密钥（推荐，操作前确认密钥已配好）
# sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
# sudo systemctl restart ssh
```

### 1.3 安装 Docker 和 Docker Compose

```bash
# Docker 官方一键脚本
curl -fsSL https://get.docker.com | sudo bash

# 加入 docker 组（免 sudo）
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker --version
docker compose version
```

> ⚠️ 如果 OpenClaw 镜像已预装 Docker，跳过即可：`docker --version`。

### 1.4 腾讯云控制台：防火墙放行端口

登录控制台 → 你的实例 → **防火墙** → **管理防火墙规则** → 添加：

| 协议 | 端口 | 来源 | 说明 |
|---|---|---|---|
| TCP | 22 | 你的本地 IP | SSH（仅限自己访问） |
| TCP | 80 | 0.0.0.0/0 | HTTP |
| TCP | 443 | 0.0.0.0/0 | HTTPS |

**不要**把 5432 / 6379 / 8000 放到公网，这些端口只在容器内部网络使用。

---

## 二、部署代码

### 2.1 上传代码

**方式 A：Git 拉取（推荐，需要先把项目推到 Gitee/GitHub）**

```bash
ssh ubuntu@81.71.89.228
mkdir -p ~/apps && cd ~/apps
git clone https://your-git-host/minigamer.git
cd minigamer
```

**方式 B：本地打包上传**

```powershell
# 在本地 Windows PowerShell
cd D:\Project\MiniGamer
tar --exclude='.git' --exclude='node_modules' --exclude='.venv' --exclude='logs' -czf minigamer.tar.gz .
scp minigamer.tar.gz ubuntu@81.71.89.228:/home/ubuntu/
```

```bash
# 服务器上解压
cd ~ && mkdir -p apps/minigamer && tar -xzf minigamer.tar.gz -C apps/minigamer && cd apps/minigamer
```

### 2.2 配置环境变量

```bash
cd ~/apps/minigamer/deploy
cp .env.example .env
vim .env   # 填入真实的微信 APPID、SECRET、数据库密码、JWT 密钥、AI Key
```

**必改项**：
- `POSTGRES_PASSWORD` — 用强密码
- `JWT_SECRET_KEY` — 至少 32 位随机字符串，可用 `openssl rand -hex 32` 生成
- `WECHAT_APPID` / `WECHAT_SECRET` — 微信小程序后台「开发设置」获取
- `AI_PROVIDER` + 对应的 `*_API_KEY`

### 2.3 启动

```bash
cd ~/apps/minigamer/deploy
docker compose up -d --build
```

首次启动会构建镜像（约 3~5 分钟）。完成后查看：

```bash
docker compose ps
# 应该看到 minigamer-pg / minigamer-redis / minigamer-app / minigamer-nginx 全部 Up

docker compose logs -f app    # 查看应用日志
```

### 2.4 验证

```bash
# 在服务器上
curl http://127.0.0.1/health
# {"status":"healthy"}

curl http://127.0.0.1/
# {"service":"MiniGamer","status":"running"}
```

本机浏览器访问：`http://81.71.89.228/health`

---

## 三、数据库迁移

首次启动后，表由 `app_env=dev` 下的 `init_db` 创建。**生产环境建议关闭 dev，改用 Alembic**：

```bash
# 进入容器执行迁移（后续新增表用 Alembic）
docker compose exec app alembic upgrade head

# 生成新的迁移（开发环境改模型后）
docker compose exec app alembic revision --autogenerate -m "add some_table"
```

---

## 四、配置 HTTPS（微信小程序强制要求）

微信小程序正式上线必须 HTTPS。流程：

1. 买一个域名，DNS 解析到 `81.71.89.228`（腾讯云 DNSPod 免费 DNS）
2. 安装 Certbot 申请免费 Let's Encrypt 证书：

```bash
sudo apt install -y certbot
# 临时停掉 nginx（因为 certbot 要用 80 端口）
docker compose stop nginx

sudo certbot certonly --standalone -d api.your-domain.com

# 证书会生成在 /etc/letsencrypt/live/api.your-domain.com/
# 复制到 deploy/certs/
sudo cp /etc/letsencrypt/live/api.your-domain.com/fullchain.pem ~/apps/minigamer/deploy/certs/
sudo cp /etc/letsencrypt/live/api.your-domain.com/privkey.pem ~/apps/minigamer/deploy/certs/
sudo chown -R $USER:$USER ~/apps/minigamer/deploy/certs/

# 打开 deploy/nginx.conf 中的 HTTPS 注释块，改 server_name
# 重启
docker compose up -d nginx
```

然后在微信小程序后台「开发 → 开发管理 → 开发设置」配置服务器域名 `https://api.your-domain.com`。

---

## 五、日常运维

### 更新代码

```bash
cd ~/apps/minigamer
git pull    # 或重新 scp
cd deploy
docker compose up -d --build app   # 只重建 app，不动数据库
```

### 查看日志

```bash
docker compose logs -f --tail=200 app
docker compose logs -f nginx
```

### 备份数据库

```bash
# 在服务器上
docker compose exec -T postgres pg_dump -U minigamer minigamer | gzip > ~/backup-$(date +%F).sql.gz
```

### 停止 / 重启

```bash
docker compose stop         # 停止
docker compose start        # 启动
docker compose restart app  # 只重启应用
docker compose down         # 停止并删除容器（数据卷保留）
```

---

## 六、故障排查

| 现象 | 排查 |
|---|---|
| `docker compose up` 卡在拉镜像 | 换国内镜像源：编辑 `/etc/docker/daemon.json` 加 `{"registry-mirrors":["https://mirror.ccs.tencentyun.com"]}` 然后 `sudo systemctl restart docker` |
| 容器启动后立即退出 | `docker compose logs app` 看具体报错，多半是 `.env` 配置错 |
| 小程序请求 CORS 报错 | 检查 `.env` 的 `CORS_ORIGINS` 是否包含 `https://servicewechat.com` |
| 微信登录返回 `mock_openid_xxx` | 说明 `WECHAT_APPID` 还没配；本地开发时这是正常行为 |
| Nginx 502 | 多半是 app 容器没起来，`docker compose ps` 确认状态 |

---

## 七、本地开发模式（不部署）

本地只起数据库和 Redis，App 直接 uvicorn 跑方便调试：

```powershell
# Windows PowerShell
cd D:\Project\MiniGamer\deploy
docker compose -f docker-compose.dev.yml up -d

cd ..\server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item ..\.env.example .env
# 编辑 .env，保持默认值即可（DB 连 127.0.0.1:5432）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器访问 `http://127.0.0.1:8000/docs` 查看交互式 API 文档。
