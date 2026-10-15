# =====================================================================
# 상품 API (Product API) — 2일 차 버전
#
# 오늘은 서버가 켜지는지 확인하는 /health와,
# 상품 목록을 조회하는 GET /products만 만듭니다.
# (상품 등록·수정·삭제는 3일 차에 추가합니다.)
#
# '#'으로 시작하는 줄은 주석(설명)이고, 컴퓨터는 이 줄을 무시합니다.
# =====================================================================

# FastAPI: 웹 API를 쉽게 만들어 주는 도구
from fastapi import FastAPI

# 가게 간판을 다는 것과 같습니다. title은 /docs 화면 위쪽에 표시됩니다.
app = FastAPI(title="Product API", version="0.1.0")

# 상품을 담아 둘 상자. 지금은 비어 있습니다.
# (3일 차에 등록 기능을 만들면 여기에 상품이 들어갑니다.)
products = {}


# 서비스가 살아 있는지 확인하는 창구입니다.
# 브라우저에서 /health 로 접속하면 {"status": "ok"}가 보입니다.
@app.get("/health")
def health():
    return {"status": "ok"}


# 전체 상품 목록 조회 창구입니다. 지금은 빈 목록 []이 나옵니다.
@app.get("/products")
def list_products():
    return list(products.values())