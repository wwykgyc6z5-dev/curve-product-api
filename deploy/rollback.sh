#!/usr/bin/env bash
# =====================================================================
# 운영 서버에서 실행될 롤백 스크립트
# =====================================================================
set -euo pipefail

ACTIVE_FILE=/etc/nginx/curve-active.conf

# 1) 지금 운영 중인 색과 직전 색 확인
if grep -q 8001 "$ACTIVE_FILE"; then
  CURRENT=blue;  OLD=green; OLD_PORT=8002
else
  CURRENT=green; OLD=blue;  OLD_PORT=8001
fi

# 2) 직전 색이 살아 있어야 되돌릴 수 있음
if ! curl -fsS "http://127.0.0.1:$OLD_PORT/health" >/dev/null; then
  echo "직전 버전($OLD)이 실행 중이 아니라 롤백할 수 없음"
  exit 1
fi

# 3) nginx를 직전 색으로 전환
echo "proxy_pass http://127.0.0.1:$OLD_PORT;" | sudo tee "$ACTIVE_FILE" >/dev/null
sudo nginx -t
sudo systemctl reload nginx

echo "롤백 완료: $CURRENT → $OLD"