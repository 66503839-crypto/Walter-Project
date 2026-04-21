# =============================================================================
# MiniGamer 本地打包 + 上传脚本（仅在个人电脑使用）
# =============================================================================
# 用法：在项目根目录运行
#   cd D:\Project\MiniGamer
#   .\deploy\upload.ps1
# =============================================================================

param(
    [string]$ServerIP = "81.71.89.228",
    [string]$ServerUser = "ubuntu",
    [string]$RemoteHome = "/home/ubuntu"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root

$ArchiveName = "minigamer.tar.gz"

Write-Host "==> 打包工程..." -ForegroundColor Cyan
tar --exclude=".git" `
    --exclude=".venv" `
    --exclude="node_modules" `
    --exclude="__pycache__" `
    --exclude="miniprogram_npm" `
    --exclude=".pytest_cache" `
    --exclude="client/dist" `
    --exclude="logs" `
    --exclude="*.tar.gz" `
    -czf $ArchiveName client deploy scripts server README.md .env.example

$size = [math]::Round((Get-Item $ArchiveName).Length / 1KB, 1)
Write-Host "   -> $ArchiveName ($size KB)" -ForegroundColor Green

Write-Host "==> 上传到 ${ServerUser}@${ServerIP}:${RemoteHome}/ ..." -ForegroundColor Cyan
scp $ArchiveName "${ServerUser}@${ServerIP}:${RemoteHome}/"

Write-Host "==> 远程解压..." -ForegroundColor Cyan
ssh "${ServerUser}@${ServerIP}" "mkdir -p ~/apps/minigamer && tar -xzf ~/$ArchiveName -C ~/apps/minigamer && echo '解压完成，文件清单：' && ls ~/apps/minigamer"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host " 上传完成！下一步在服务器上执行：" -ForegroundColor Green
Write-Host "   ssh ${ServerUser}@${ServerIP}" -ForegroundColor Yellow
Write-Host "   bash ~/apps/minigamer/deploy/server-setup.sh" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Green

Pop-Location
