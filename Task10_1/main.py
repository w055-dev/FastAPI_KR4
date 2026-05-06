from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional

class ErrorResponse(BaseModel):
    status_code: int
    message: str
    error_type: str
    details: Optional[dict] = None

class ProductNotFound(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        self.status_code = 404
        super().__init__(f"Продукт с ID {product_id} не найден")

class OutOfStock(Exception):
    def __init__(self, product_name: str, available: int):
        self.product_name = product_name
        self.available = available
        self.status_code = 422
        super().__init__(f"'{product_name}' нет в наличии")

app = FastAPI()

@app.exception_handler(ProductNotFound)
async def product_not_found_handler(request: Request, exc: ProductNotFound):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            status_code=404,
            message=str(exc),
            error_type="ProductNotFound",
            details={"product_id": exc.product_id}
        ).model_dump()
    )

@app.exception_handler(OutOfStock)
async def out_of_stock_handler(request: Request, exc: OutOfStock):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            status_code=422,
            message=str(exc),
            error_type="OutOfStock",
            details={
                "product_name": exc.product_name,
                "available": exc.available
            }
        ).model_dump()
    )

products = {
    1: {"id": 1, "name": "Ноутбук", "price": 999.99, "stock": 10},
    2: {"id": 2, "name": "Книга", "price": 19.99, "stock": 50},
    3: {"id": 3, "name": "Кофе", "price": 5.99, "stock": 0},
}

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    if product_id not in products:
        raise ProductNotFound(product_id)
    return {"data": products[product_id]}

@app.post("/orders")
async def create_order(product_id: int, quantity: int):
    if product_id not in products:
        raise ProductNotFound(product_id)
    product = products[product_id]
    if product["stock"] <= 0:
        raise OutOfStock(product["name"], product["stock"])
    if quantity > product["stock"]:
        raise OutOfStock(
            product["name"], 
            product["stock"]
        )
    return {
        "message": f"Заказ на {quantity} шт. '{product['name']}' создан",
        "total_price": product["price"] * quantity
    }
