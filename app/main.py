# =====================================================================
# 상품 API (Product API)



from fastapi import FastAPI, HTTPException, Response, status


from pydantic import BaseModel, Field

app = FastAPI(title="Product API", version="0.1.0")


# --- 데이터 양식 정의 --------------------------------------------------
class ProductIn(BaseModel):
    # 상품 이름
    name: str = Field(min_length=1, max_length=100)

    # 가격
    price: int = Field(ge=0, description="원 단위 가격")

    # 재고 수량
    stock: int = Field(default=0, ge=0, description="재고 수량")


# 저장된 상품 양식
class Product(ProductIn):
    id: int


# --- 데이터 저장소 -----------------------------------------------------

products: dict[int, Product] = {}

next_id = 1


def reset_store() -> None:
    """저장소를 텅 비우고 번호를 1번으로 되돌립니다.
    """
    global next_id
    products.clear()
    next_id = 1


def get_or_404(product_id: int) -> Product:
    """번호로 상품을 찾아 돌려줍니다. 없으면 404 오류를 보냅니다.
    """
    product = products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product



# 서비스가 살아 있는지 확인용
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# 전체 상품 목록 조회
@app.get("/products")
def list_products() -> list[Product]:
    return list(products.values())


# 새 상품 등록
@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn) -> Product:
    global next_id

    product = Product(id=next_id, **payload.model_dump())

    products[product.id] = product
    next_id += 1
    return product


# 특정 상품 조회
@app.get("/products/{product_id}")
def get_product(product_id: int) -> Product:
    return get_or_404(product_id)


# 상품 정보 수정
@app.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductIn) -> Product:
    get_or_404(product_id)

    product = Product(id=product_id, **payload.model_dump())
    products[product_id] = product
    return product


# 상품 삭제
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int) -> Response:
    get_or_404(product_id)   # 있는 상품인지 확인
    del products[product_id]  # 저장소에서 지우기
    return Response(status_code=status.HTTP_204_NO_CONTENT)