# =====================================================================
# 상품 API 자동 테스트
# =====================================================================

import pytest

# TestClient: API에 가짜 요청을 보내기
from fastapi.testclient import TestClient

from app.main import app, reset_store

client = TestClient(app)


# --- 매 테스트 전후 정리 -----------------------------------------------
# 데이터가 섞이지 않게 테스트 전후 저장소 삭제
@pytest.fixture(autouse=True)
def clean_store():
    reset_store()
    yield
    reset_store()


# 아무것도 안 넘기면 "무선 마우스, 25000원"으로 등록
def create(name="무선 마우스", price=25000, **extra):
    return client.post("/products", json={"name": name, "price": price, **extra})


# --- 상태 확인 ---------------------------------------------------------

def test_health():
    # /health에 물어보면 200(성공)과 {"status": "ok"}가 와야 한다
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# --- 목록 조회 ---------------------------------------------------------

def test_list_empty():
    # 아무것도 등록 안 했으면 빈 목록 []이 와야 한다
    res = client.get("/products")
    assert res.status_code == 200
    assert res.json() == []


# --- 등록 --------------------------------------------------------------

def test_create_product():
    # 재고 10개로 등록하면 201(생성됨)과 1번 번호가 붙은 상품이 돌아와야 한다
    res = create(stock=10)
    assert res.status_code == 201
    assert res.json() == {"id": 1, "name": "무선 마우스", "price": 25000, "stock": 10}


def test_create_defaults_stock_to_zero():
    # 재고를 안 보내면 자동으로 0이어야 한다
    assert create().json()["stock"] == 0


def test_create_assigns_increasing_ids():
    # 두 개 등록하면 번호가 1, 2 순서로 붙고, 목록에 2개가 있어야 한다
    assert create("키보드").json()["id"] == 1
    assert create("모니터").json()["id"] == 2
    assert len(client.get("/products").json()) == 2


# --- 잘못된 입력 막기 -------------------

def test_create_rejects_empty_name():
    # 이름이 공백일 시 거절
    assert create(name="").status_code == 422


def test_create_rejects_missing_price():
    # 가격을 아예 안 보내면 거절
    res = client.post("/products", json={"name": "키보드"})
    assert res.status_code == 422



@pytest.mark.parametrize("field", ["price", "stock"])
def test_create_rejects_negative_numbers(field):
    payload = {"name": "키보드", "price": 1000, "stock": 1, field: -1}
    res = client.post("/products", json=payload)
    assert res.status_code == 422


# --- 조회 ---------------------------------------------------------

def test_get_product():
    # 등록한 1번 상품을 조회하면 그 이름이 나와야 한다
    create()
    res = client.get("/products/1")
    assert res.status_code == 200
    assert res.json()["name"] == "무선 마우스"


def test_get_missing_product_returns_404():
    # 없는 999번을 조회하면 404(없음)여야 한다
    res = client.get("/products/999")
    assert res.status_code == 404
    assert res.json() == {"detail": "Product not found"}


# --- 수정 --------------------------------------------------------------

def test_update_product():
    # 가격과 재고를 바꾸면 바뀐 값이 반환되어야 함
    create(stock=10)
    res = client.put("/products/1", json={"name": "무선 마우스", "price": 22000, "stock": 7})
    assert res.status_code == 200
    assert res.json() == {"id": 1, "name": "무선 마우스", "price": 22000, "stock": 7}
    assert client.get("/products/1").json()["stock"] == 7


def test_update_missing_product_returns_404():
    
    res = client.put("/products/999", json={"name": "없음", "price": 0})
    assert res.status_code == 404


# --- 삭제 --------------------------------------------------------------

def test_delete_product():
    # 삭제시 204
    create()
    assert client.delete("/products/1").status_code == 204
    assert client.get("/products/1").status_code == 404


def test_delete_missing_product_returns_404():
    # 존재하지 않는 상품 삭제시 반환
    assert client.delete("/products/999").status_code == 404