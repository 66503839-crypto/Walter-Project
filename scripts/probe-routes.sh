#!/usr/bin/env bash
set +e

echo '=== FastAPI 注册的所有路由 ==='
docker exec minigamer-app python <<'PYEOF'
from app.main import app
for r in app.routes:
    if hasattr(r, "path"):
        methods = ",".join(r.methods) if hasattr(r, "methods") and r.methods else "?"
        print(f"  [{methods}] {r.path}")
PYEOF

echo
echo '=== 从 nginx 走各种路径的响应 ==='
for p in /mg-api/health /mg-api/v1/health /mg-api/ /mg-api /mg-api/v1/auth/wx-login; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1${p}")
    echo "  $p -> HTTP $code"
done

echo
echo '=== 直接打 FastAPI 的相同路径 ==='
for p in /health /api/health /api/v1/health /api/v1/auth/wx-login; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8000${p}")
    echo "  $p -> HTTP $code"
done
