# 本地开发快速启动（Windows PowerShell）
#
# 一键启动 PG/Redis + 安装依赖 + 运行服务端
#
# 用法：在项目根目录下右键「在终端运行」，或：
#   cd D:\Project\MiniGamer
#   .\scripts\dev.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> 启动 PostgreSQL + Redis 容器..." -ForegroundColor Cyan
Push-Location "$Root\deploy"
docker compose -f docker-compose.dev.yml up -d
Pop-Location

Push-Location "$Root\server"

if (-not (Test-Path ".venv")) {
    Write-Host "==> 创建 Python 虚拟环境..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host "==> 激活虚拟环境 & 安装依赖..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet

if (-not (Test-Path ".env")) {
    Write-Host "==> 生成 .env（从 .env.example 复制）..." -ForegroundColor Yellow
    Copy-Item "$Root\.env.example" ".env"
    # 本地开发用 dev 数据库密码
    (Get-Content .env) -replace 'POSTGRES_PASSWORD=.*', 'POSTGRES_PASSWORD=dev_password' `
                       -replace 'DATABASE_URL=.*', 'DATABASE_URL=postgresql+asyncpg://minigamer:dev_password@127.0.0.1:5432/minigamer' `
        | Set-Content .env
}

Write-Host "==> 启动服务端（http://127.0.0.1:8000/docs 查看 API）..." -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Pop-Location
