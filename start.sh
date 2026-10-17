#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "🚀 Arrancando Test Router…"
if command -v xdg-open &> /dev/null; then
  (sleep 1 && xdg-open "http://localhost:8000") &
fi
python3 server.py
