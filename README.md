# Product API

상품 이름·가격·재고 수량을 관리하는 REST API입니다.

## 기술 구성

| 구분 | 사용 기술 | 선택 이유 |
| --- | --- | --- |
| 언어/프레임워크 | Python, FastAPI | 코드가 짧고, API 문서(`/docs`)가 자동 생성됨 |
| 테스트 | pytest | Python 표준에 가까운 테스트 도구 |
| 협업 | Jira, Confluence, GitHub | 이슈 → 커밋 → PR → 문서까지 한 흐름으로 추적 |

## API 목록

| 메서드 | 경로 | 설명 | 성공 코드 |
| --- | --- | --- | --- |
| GET | `/health` | 서비스 상태 확인 | 200 |
| GET | `/products` | 전체 상품 조회 | 200 |
| POST | `/products` | 새 상품 등록 | 201 |
| GET | `/products/{id}` | 특정 상품 조회 | 200 (없으면 404) |
| PUT | `/products/{id}` | 상품 정보 수정 | 200 (없으면 404) |
| DELETE | `/products/{id}` | 상품 삭제 | 204 (없으면 404) |

요청 본문 예시:

```json
{ "name": "무선 마우스", "price": 25000, "stock": 10 }
```

`name`(1~100자)과 `price`는 필수이고, `stock`은 생략하면 0입니다.
가격이나 재고가 음수이거나 이름이 비어 있으면 422 오류를 반환합니다.
데이터는 메모리에 저장되므로 서버를 재시작하면 초기화됩니다.

## 로컬에서 실행하기

Python 3.13 이상이 필요합니다.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

브라우저에서 http://localhost:8000/docs 를 열면 API를 직접 호출해 볼 수 있습니다.

## 테스트 실행

```bash
pytest -v
```

정상 요청뿐 아니라 존재하지 않는 항목(404), 잘못된 입력(422) 같은 오류 상황도 검사합니다.

## 폴더 구조

```
app/main.py              API 코드
tests/test_products.py   단위 테스트
requirements.txt         앱 실행에 필요한 라이브러리
requirements-dev.txt     테스트까지 할 때 필요한 라이브러리
.github/                 PR 템플릿
Dockerfile               컨테이너 이미지 정의
compose.yaml             Docker Compose 실행 설정
```

## 작업 규칙 (GitHub Flow)

- 모든 작업은 Jira 이슈에서 시작합니다.
- 브랜치 이름: `feature/<이슈키>-<짧은설명>` (예: `feature/MT-12-stock-validation`)
- 커밋 메시지 앞에 이슈 키를 붙입니다. (예: `MT-12 재고 음수 검증 추가`)
- `main`에는 직접 푸시하지 않고 PR로만 병합합니다.
- PR을 열면 `.github/pull_request_template.md` 양식이 자동으로 채워집니다.

## Docker로 실행하기

```bash
docker compose up -d --build       # 빌드 후 백그라운드 실행
curl http://localhost:8000/health  # {"status":"ok"}
docker compose down                # 종료
```

`python:3.13-slim` 바탕을 써서 이미지 크기를 1.68GB → 272MB로 줄였고,
컨테이너는 root가 아닌 `appuser` 계정으로 실행되며 `/health`로 상태 검사를 합니다.