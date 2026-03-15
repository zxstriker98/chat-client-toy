#!/bin/bash
# Start chat-client-toy LLM gateway
# Usage:
#   ./start.sh                              → default model, no restaurant
#   ./start.sh llama3.2:3b                  → specific model
#   ./start.sh llama3.1:8b 8100 delhi-darbar → model + port + restaurant
cd "$(dirname "$0")"

MODEL="${1:-llama3.1:8b}"
PORT="${2:-8100}"
RESTAURANT="${3:-}"

# Kill existing instance
[ -f server.pid ] && kill "$(cat server.pid)" 2>/dev/null

echo "$(date '+%Y-%m-%d %H:%M:%S') Starting chat-client-toy (model=$MODEL, port=$PORT)" | tee -a server.log
RESTAURANT_FLAG=""
[ -n "$RESTAURANT" ] && RESTAURANT_FLAG="--restaurant $RESTAURANT"
UV_INDEX_URL=https://pypi.org/simple/ PYTHONUNBUFFERED=1 uv run python server.py --model "$MODEL" --port "$PORT" $RESTAURANT_FLAG >> server.log 2>&1 &
echo $! > server.pid
echo "PID $(cat server.pid) — logs → server.log"

# Wait for it to be ready
for i in $(seq 1 10); do
  sleep 1
  if grep -q "chat-client-toy gateway" server.log 2>/dev/null && kill -0 "$(cat server.pid)" 2>/dev/null; then
    echo ""
    echo "════════════════════════════════════════════════"
    echo "  🧠 chat-client-toy is live!"
    echo ""
    echo "  Model:    $MODEL"
    echo "  Endpoint: http://localhost:$PORT/v1/chat/completions"
    echo "════════════════════════════════════════════════"
    echo ""
    exit 0
  fi
done

echo "⚠️  Server may not have started — check server.log"
