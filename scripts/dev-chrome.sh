#!/usr/bin/env bash
# Отдельное окно Google Chrome с CDP для IronBee DevTools.
# IronBee подключается к http://127.0.0.1:9222 (см. .vscode/settings.json).

set -euo pipefail

PORT="${IRONBEE_CDP_PORT:-9222}"
URL="${1:-http://127.0.0.1:5000/}"
PROFILE="${XDG_CACHE_HOME:-$HOME/.cache}/flask-blog-chrome-profile"

mkdir -p "$PROFILE"

if ss -tln | grep -q ":${PORT} "; then
  echo "CDP уже слушает порт ${PORT}. Откройте ${URL} в существующем окне или освободите порт."
  exit 0
fi

echo "Запуск Chrome (CDP :${PORT}) → ${URL}"
exec google-chrome \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${PROFILE}" \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  "${URL}"
