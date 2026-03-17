#!/bin/bash
# Stop chat-client-toy gateway
cd "$(dirname "$0")"

if [ -f server.pid ]; then
  PID=$(cat server.pid)
  kill "$PID" 2>/dev/null && echo "Stopped chat-client-toy (PID $PID)" || echo "Process $PID not running"
  rm -f server.pid
else
  echo "No server.pid found"
fi
