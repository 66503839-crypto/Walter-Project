#!/usr/bin/env bash
# 探测 TokenPlan 实际路由到哪些模型
set +e

# 从 .env 读 key
source /data/minigamer/.env

KEY="$TOKENPLAN_API_KEY"
URL="$TOKENPLAN_BASE_URL/chat/completions"

ask() {
    local tag="$1"
    local question="$2"
    echo "===== $tag ====="
    echo "问题：$question"
    resp=$(curl -s "$URL" \
        -H "Authorization: Bearer $KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"tc-code-latest\",
            \"messages\": [{\"role\":\"user\",\"content\":\"$question\"}],
            \"stream\": false
        }")
    # 提取 model + content 前 100 字
    echo "返回 model 字段: $(echo "$resp" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("model","?"))')"
    echo "返回 content 前 120 字: $(echo "$resp" | python3 -c 'import sys,json; d=json.load(sys.stdin); c=d.get("choices",[{}])[0].get("message",{}).get("content",""); print(c[:120])')"
    echo
}

ask "Q1 自我认知" "你是什么模型？"
ask "Q2 代码问题" "用 Python 写一个冒泡排序"
ask "Q3 数学问题" "123*456 等于多少？"
ask "Q4 直接问厂家" "请用一句话告诉我你是哪家公司开发的，叫什么名字，参数量多少？"

echo "===== 查 TokenPlan 是否返回可用模型列表 ====="
curl -s "$TOKENPLAN_BASE_URL/models" -H "Authorization: Bearer $KEY" | python3 -c 'import sys,json; d=json.load(sys.stdin); data=d.get("data",[]); print(f"可用模型数: {len(data)}"); [print(f"  - {m.get(\"id\")}") for m in data[:20]]' 2>&1 | head -30
