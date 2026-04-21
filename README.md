# MiniGamer — 微信小程序助手

> 综合型个人助手：效率工具 + AI 对话 + 信息聚合 + 业务打卡

## 项目结构

```
MiniGamer/
├── client/                 # 微信小程序客户端（TypeScript + 原生）
│   ├── miniprogram/        # 小程序源码
│   ├── typings/            # 类型定义
│   ├── project.config.json
│   └── tsconfig.json
├── server/                 # 服务端（Python 3.11 + FastAPI）
│   ├── app/
│   │   ├── api/            # 路由层
│   │   ├── core/           # 配置、安全、中间件
│   │   ├── db/             # 数据库连接、模型
│   │   ├── schemas/        # Pydantic 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py
│   ├── alembic/            # 数据库迁移
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── deploy/                 # 部署脚本
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── deploy.md           # 部署到腾讯云详细步骤
├── docs/                   # 项目文档
├── .gitignore
├── .env.example
└── README.md
```

## 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 客户端 | TypeScript + 原生小程序 | 类型安全、轻量 |
| 服务端 | Python 3.11 + FastAPI | 异步、生态好、易接 AI |
| 数据库 | PostgreSQL 16 | 关系型业务数据 |
| 缓存 | Redis 7 | 会话、限流、缓存 |
| ORM | SQLAlchemy 2.0 (async) | 异步 ORM |
| 迁移 | Alembic | 数据库版本管理 |
| 认证 | JWT + 微信 code2session | 微信登录 |
| AI | 多 Provider 抽象 | OpenAI / DeepSeek / 通义 可切换 |
| 部署 | Docker Compose + Nginx | 单机一键部署 |

## 功能模块

### ✅ 本版本已实现
- [x] 微信登录（wx.login + 后端 JWT 签发）
- [x] TODO 增删改查（示例业务）
- [x] AI 对话（流式返回，多 Provider 可切换）
- [x] 基础 HUD：用户信息、登出

### 🔜 后续扩展
- [ ] 日程 / 备忘录
- [ ] 信息聚合（天气 / 快递 / 新闻）
- [ ] 记账 / 健身打卡
- [ ] 学习计划

## 快速开始

### 本地开发

1. **服务端**
   ```bash
   cd server
   python -m venv .venv
   .venv\Scripts\activate       # Windows
   pip install -r requirements.txt
   cp ../.env.example .env
   # 编辑 .env 填入 WECHAT_APPID / SECRET / DB 连接串等
   docker compose -f ../deploy/docker-compose.dev.yml up -d postgres redis
   alembic upgrade head
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **客户端**
   - 用微信开发者工具导入 `client/` 目录
   - 在 `client/miniprogram/config.ts` 中把 `API_BASE_URL` 改为 `http://127.0.0.1:8000`
   - 勾选「不校验合法域名」（开发阶段）

### 部署到腾讯云

见 [`deploy/deploy.md`](./deploy/deploy.md)

## 服务器信息

| 项 | 值 |
|---|---|
| 公网 IP | 81.71.89.228 |
| 内网 IP | 10.1.0.11 |
| 系统 | Ubuntu Server 24.04 LTS |
| 规格 | 2核 4GB / 60GB SSD / 200Mbps |
| 区域 | 广州七区 |

## 许可

MIT
