from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, noload, joinedload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from src.models import Product, Aisle
from src.database import SessionLocal
from box import BoxList

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
    href: str = Field()
    src: str = Field()
    alt: str = Field()
    price: str = Field()
    aisle_id: int = Field()


class ProductPatch(BaseModel):
    name: str = Field(default=None)
    product_id: int = Field(default=None)
    rank: int = Field(default=None)
    href: str = Field(default=None)
    src: str = Field(default=None)
    alt: str = Field(default=None)
    price: str = Field(default=None)
    aisle_id: int = Field(default=None)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_products(db: db_dependency):
    return db.query(Product).all()


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def read_product(
    db: db_dependency, product_id: int = Path(gt=0), with_sections: bool = False
):
    if not with_sections:
        product_model = (
            db.query(Product)
            .options(noload("*"))
            .filter(Product.product_id == product_id)
            .first()
        )
    else:
        product_model = (
            db.query(Product)
            .options(joinedload(Product.featured_products))
            .options(joinedload(Product.related_items))
            .options(joinedload(Product.often_bought_with))
            .filter(Product.product_id == product_id)
            .first()
        )
        featured_product_ids = [
            x.child_product_id for x in BoxList(product_model.featured_products)
        ]
        related_item_ids = [
            x.child_product_id for x in BoxList(product_model.related_items)
        ]
        often_bought_with_ids = [
            x.child_product_id for x in BoxList(product_model.often_bought_with)
        ]
        sections = {
            "featured_products": (
                db.query(Product)
                .filter(Product.product_id.in_(featured_product_ids))
                .all()
            ),
            "related_items": (
                db.query(Product).filter(Product.product_id.in_(related_item_ids)).all()
            ),
            "often_bought_with": (
                db.query(Product)
                .filter(Product.product_id.in_(often_bought_with_ids))
                .all()
            ),
        }
        for section in sections.values():
            for product in section:
                product.href
        setattr(product_model, "sections", sections)

    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    product_model.href
    product_model.remove_section_relationships()
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
    db.refresh(product_model)


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
    product_model.src = product_request.src
    product_model.alt = product_request.alt
    product_model.price = product_request.price

    db.add(product_model)
    db.commit()
    db.refresh(product_model)


@router.patch("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_product(
    db: db_dependency, product_request: ProductPatch, product_id: int = Path(gt=0)
):
    product_model = db.query(Product).filter(Product.product_id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    if product_request.name:
        product_model.name = product_request.name
    if product_request.product_id:
        product_model.product_id = product_request.product_id
    if product_request.rank:
        product_model.rank = product_request.rank
    if product_request.src:
        product_model.src = product_request.src
    if product_request.alt:
        product_model.alt = product_request.alt
    if product_request.price:
        product_model.price = product_request.price

    db.add(product_model)
    db.commit()
    db.refresh(product_model)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(db: db_dependency, product_id: int):
    product_model = db.query(Product).filter(Product.product_id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    db.query(Product).filter(Product.product_id == product_id).delete()
    db.commit()
