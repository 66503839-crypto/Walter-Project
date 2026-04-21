# MiniGamer 部署操作手册（服务器端执行版）

> 本手册适用于：**你不方便在当前机器上直接 SSH** 的场景（比如 iOA 拦截、临时换设备等）。
> 核心思路：**把代码和脚本弄到服务器上，然后在服务器上一条命令搞定。**
> 服务器：`ubuntu@81.71.89.228`

---

## 一、当前工程已经准备好的东西

以下文件已就绪，不需要你再动：

| 文件 | 说明 |
|---|---|
| `deploy/.env` | 生产环境变量（AppID / Qwen Key / JWT / DB 密码等都填好了） |
| `deploy/docker-compose.yml` | PG + Redis + FastAPI + Nginx 四件套 |
| `deploy/nginx.conf` | Nginx 反代到 FastAPI |
| `deploy/daemon.json` | Docker 腾讯云镜像加速配置 |
| `deploy/server-setup.sh` | **一键部署脚本**（幂等、带自检） |
| `server/` | 后端代码 |
| `client/miniprogram/config.ts` | 已指向 `http://81.71.89.228/api/v1` |

---

## 二、把代码弄到服务器（三选一）

### 方式 A：用个人电脑 + OpenSSH（最简单，推荐）

在**个人电脑**的 PowerShell / 终端里，进入项目根目录：

```powershell
cd D:\Project\MiniGamer   # 如果项目也在个人电脑上
# 如果项目只在公司电脑上，先用 U 盘 / 网盘把整个 MiniGamer 目录拷到个人电脑

# 1) 打包（排除无关大目录）
tar --exclude=".git" --exclude=".venv" --exclude="node_modules" `
    --exclude="__pycache__" --exclude="miniprogram_npm" `
    --exclude=".pytest_cache" --exclude="client/dist" --exclude="logs" `
    -czf minigamer.tar.gz client deploy scripts server README.md .env.example

# 2) 上传
scp minigamer.tar.gz ubuntu@81.71.89.228:/home/ubuntu/

# 3) 登录服务器解压 + 跑脚本
ssh ubuntu@81.71.89.228
# —— 以下在服务器上 ——
mkdir -p ~/apps/minigamer
tar -xzf ~/minigamer.tar.gz -C ~/apps/minigamer
bash ~/apps/minigamer/deploy/server-setup.sh
```

### 方式 B：用腾讯云控制台「网页终端」（无需本地 SSH）

1. 登录腾讯云控制台：<https://console.cloud.tencent.com/lighthouse>
2. 找到实例 `lhins-28n94ssr` → 点「登录」→ 选「**VNC 登录**」或「**网页终端**」
3. 会在浏览器里打开一个终端，**不经过 iOA**
4. 把项目推到 Gitee / GitHub 后，在网页终端里：
   ```bash
   cd ~ && mkdir -p apps && cd apps
   git clone https://gitee.com/你的账号/minigamer.git
   cd minigamer
   # 然后手动把本地 deploy/.env 内容粘进去（网页终端支持复制粘贴）
   nano deploy/.env   # 粘贴 -> Ctrl+O 保存 -> Ctrl+X 退出
   bash deploy/server-setup.sh
   ```

### 方式 C：直接用腾讯云控制台的「文件上传」功能

1. 轻量应用服务器控制台 → 实例详情 → 「**文件上传**」
2. 上传本地打包好的 `minigamer.tar.gz`
3. 然后走方式 A 的第 3 步（网页终端登录解压）

---

## 三、一键脚本做了什么

`server-setup.sh` 幂等执行以下操作，你不用记每一步：

1. ✅ 检查 Docker 是否已装，没装就走官方脚本装
2. ✅ 配置腾讯云镜像加速（`mirror.ccs.tencentyun.com`），避免拉镜像慢
3. ✅ 校验 `.env` 里关键字段没留占位符
4. ✅ `docker compose pull` + `up -d --build`
5. ✅ 轮询健康检查
6. ✅ 打印容器状态 + HTTP 自检结果 + 下一步提示

**重复跑这个脚本是安全的**——比如你改了 `.env`，重新 `bash deploy/server-setup.sh` 就生效。

---

## 四、脚本跑完后你要做的两件事

### 1. 腾讯云控制台：放行 80 端口

控制台 → 实例 → **防火墙** → 添加规则：

| 协议 | 端口 | 来源 | 说明 |
|---|---|---|---|
| TCP | 80 | 0.0.0.0/0 | HTTP |

**不要**放行 5432/6379/8000，那些只在容器内部用。

### 2. 浏览器验证

打开：<http://81.71.89.228/health>
**期望看到**：`{"status":"healthy"}`

如果看到 → 后端 OK，可以去微信开发者工具试了 ✅
如果打不开 → 看第六节「故障排查」

---

## 五、微信开发者工具联调

1. 打开 `client/` 工程
2. **详情 → 本地设置 → 勾选「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」**
3. **清缓存**（工具栏「清除缓存 → 全部清除」）
4. **重新编译**
5. 首页应该不再是"你好，游客"，登录 toast 也不会再弹

---

## 六、故障排查

| 现象 | 处理 |
|---|---|
| `bash: /home/.../server-setup.sh: /usr/bin/env: 'bash\r': No such file or directory` | Windows CRLF 污染，执行 `sed -i 's/\r$//' deploy/server-setup.sh` 后再跑 |
| `docker compose up` 卡在拉镜像 | 已配腾讯云加速，如还慢检查 `sudo cat /etc/docker/daemon.json` |
| 浏览器 `http://81.71.89.228/health` 打不开 | 99% 是防火墙没放行 80（第四节第 1 步） |
| 打开了但 502 | `sudo docker compose logs app` 看 app 容器报错 |
| `mock_openid_xxx` | `.env` 的 `WECHAT_APPID` 没填好 |

### 看实时日志

```bash
cd ~/apps/minigamer/deploy
sudo docker compose logs -f app
sudo docker compose logs -f nginx
```

### 重启 / 停止

```bash
sudo docker compose restart app    # 只重启后端
sudo docker compose down           # 停掉（数据卷保留）
sudo docker compose up -d          # 再起来
```

---

## 七、后续更新代码

每次本地改代码后：

```powershell
# 本地：重打包 + 上传
cd D:\Project\MiniGamer
tar --exclude=".git" --exclude=".venv" --exclude="node_modules" -czf minigamer.tar.gz client deploy scripts server
scp minigamer.tar.gz ubuntu@81.71.89.228:/home/ubuntu/
```

```bash
# 服务器：解压覆盖 + 重启 app
ssh ubuntu@81.71.89.228
tar -xzf ~/minigamer.tar.gz -C ~/apps/minigamer
cd ~/apps/minigamer/deploy
sudo docker compose up -d --build app   # 只重建 app，PG/Redis 不动
```
