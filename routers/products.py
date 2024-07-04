from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Product, Aisle
from database import SessionLocal

# from .auth import get_current_user

router = APIRouter(
    #
    prefix="/products",
    tags=["products"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class ProductRequest(BaseModel):
    name: str = Field()
    product_id: int = Field()
    rank: int = Field()
    quantity: str = Field()
    href: str = Field()
    src: str = Field()
    alt: str = Field()
    price: str = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_products(db: db_dependency):
    return db.query(Product).all()


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def read_product(db: db_dependency, product_id: int = Path(gt=0)):
    product_model = db.query(Product).filter(Product.product_id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product_model


@router.get("/by_aisle/{aisle_id}", status_code=status.HTTP_200_OK)
async def read_products_by_aisle(db: db_dependency, aisle_id: int = Path(gt=0)):
    products = db.query(Product).filter(Product.aisle_id == aisle_id).all()
    if not len(products):
        raise HTTPException(status_code=404, detail="Aisle not found.")
    return products


@router.get("/by_department/{department_id}", status_code=status.HTTP_200_OK)
async def read_products_by_department(
    db: db_dependency, department_id: int = Path(gt=0)
):
    products = (
        db.query(Product).join(Aisle).filter(Aisle.department_id == department_id).all()
    )
    if not len(products):
        raise HTTPException(status_code=404, detail="Department not found.")
    return products


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dependency, product_request: ProductRequest):
    product_model = Product(**product_request.model_dump())
    db.add(product_model)
    db.commit()


@router.put("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(
    db: db_dependency, product_request: ProductRequest, product_id: int = Path(gt=0)
):
    product_model = db.query(Product).filter(Product.product_id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    product_model.name = product_request.name
    product_model.product_id = product_request.product_id
    product_model.rank = product_request.rank
    product_model.quantity = product_request.quantity
    product_model.href = product_request.href
    product_model.src = product_request.src
    product_model.alt = product_request.alt
    product_model.price = product_request.price

    db.add(product_model)
    db.commit()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(db: db_dependency, product_id: int):
    product_model = db.query(Product).filter(Product.product_id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    db.query(Product).filter(Product.product_id == product_id).first().delete()
