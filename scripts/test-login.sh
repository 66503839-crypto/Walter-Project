#!/usr/bin/env bash
set +e

echo '=== 1. 走 nginx（对外路径） POST wx-login ==='
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"code":"test_cvm_001"}' \
     http://127.0.0.1/mg-api/v1/auth/wx-login
echo
echo

echo '=== 2. 直连 app（对内路径） POST wx-login ==='
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"code":"test_cvm_002"}' \
     http://127.0.0.1:8000/api/v1/auth/wx-login
echo
echo

echo '=== 3. app 容器最近日志 ==='
docker compose -f /data/minigamer/app/deploy/docker-compose.internal.yml --env-file /data/minigamer/.env logs app --tail=10
