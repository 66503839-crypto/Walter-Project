#!/usr/bin/env bash
# 探测 Docker Compose 安装情况（只读，无副作用）
set +e

echo '=== 已安装 docker 相关包 ==='
rpm -qa | grep -i docker

echo
echo '=== 仓库可用的 compose 包 ==='
dnf list available 'docker-compose*' 2>&1 | tail -10
dnf list available 'compose*' 2>&1 | tail -10

echo
echo '=== cli-plugins 目录状态 ==='
for d in /usr/libexec/docker/cli-plugins /usr/lib/docker/cli-plugins /usr/local/lib/docker/cli-plugins /root/.docker/cli-plugins; do
    echo "--- $d ---"
    ls -la "$d" 2>&1
done

echo
echo '=== docker 二进制位置 ==='
command -v docker
readlink -f "$(command -v docker)"

echo
echo '=== 系统架构 ==='
uname -m
