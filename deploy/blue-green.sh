#!/usr/bin/env bash
# =====================================================================
# Blue-Green 배포 스크립트 (운영 서버에서 실행)
# 사용법: bash blue-green.sh <이미지 주소>
#
# blue  = 127.0.0.1:8001 / green = 127.0.0.1:8002
# =====================================================================
set -euo pipefail

IMAGE="$1"
TAG="${IMAGE##*:}"
ACTIVE_FILE=/etc/nginx/curve-active.conf

# 1) 지금 운영 중인 색 확인하여 반대쪽 색에 새 버전을 띄움
if grep -q 8001 "$ACTIVE_FILE"; then
  CURRENT=blue;  NEW=green; NEW_PORT=8002
else
  CURRENT=green; NEW=blue;  NEW_PORT=8001
fi
echo "현재 운영: $CURRENT → 새 버전은 $NEW (포트 $NEW_PORT)"

# 2) 새 색 컨테이너 실행 (localhost로)
docker pull "$IMAGE"
docker rm -f "api-$NEW" 2>/dev/null || true
docker run -d --name "api-$NEW" --restart unless-stopped \
  -p "127.0.0.1:$NEW_PORT:8000" \
  -e APP_ENV=prod -e APP_VERSION="$TAG" -e APP_COLOR="$NEW" \
  "$IMAGE"

# 3) 헬스 체크: 2초 간격 최대 15번
OK=0
for i in $(seq 1 15); do
  if curl -fsS "http://127.0.0.1:$NEW_PORT/health" >/dev/null; then
    OK=1
    break
  fi
  sleep 2
done

# 실패하면 전환하지 않음(무중단)
if [ "$OK" != 1 ]; then
  echo "헬스 체크 실패 → 전환하지 않고 기존 $CURRENT 유지"
  docker rm -f "api-$NEW"
  exit 1
fi

# 4) nginx가 새 색을 보도록 바꾸고, 설정 검사 후 reload
echo "proxy_pass http://127.0.0.1:$NEW_PORT;" | sudo tee "$ACTIVE_FILE" >/dev/null
sudo nginx -t
sudo systemctl reload nginx

echo "전환 완료: 지금 운영은 $NEW (이전 $CURRENT 는 롤백용으로 남겨 둠)"