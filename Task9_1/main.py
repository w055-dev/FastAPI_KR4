from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from app.database import get_db
from app.models import Product

app = FastAPI()

class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    count: int
    description: str
    model_config = ConfigDict(from_attributes=True)

@app.get("/products/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products/", response_model=ProductResponse)
def create_product(
    title: str,
    price: float,
    count: int,
    description: str,
    db: Session = Depends(get_db)
):
    product = Product(title=title, price=price, count=count, description=description)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product