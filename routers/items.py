from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Items, Aisles
from database import SessionLocal

# from .auth import get_current_user

router = APIRouter(
    #
    prefix="/items",
    tags=["items"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class ItemRequest(BaseModel):
    name: str = Field()
    product_id: int = Field()
    quantity: str = Field()
    href: str = Field()
    src: str = Field()
    alt: str = Field()
    price: str = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_items(db: db_dependency):
    return db.query(Items).all()


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def read_item(db: db_dependency, product_id: int = Path(gt=0)):
    item_model = db.query(Items).filter(Items.product_id == product_id).first()
    if item_model is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    return item_model


@router.get("/by_aisle/{aisle_id}", status_code=status.HTTP_200_OK)
async def read_items_by_aisle(db: db_dependency, aisle_id: int = Path(gt=0)):
    items = db.query(Items).filter(Items.aisle_id == aisle_id).all()
    if not len(items):
        raise HTTPException(status_code=404, detail="Aisle not found.")
    return items


@router.get("/by_department/{department_id}", status_code=status.HTTP_200_OK)
async def read_items_by_department(db: db_dependency, department_id: int = Path(gt=0)):
    items = (
        db.query(Items).join(Aisles).filter(Aisles.department_id == department_id).all()
    )
    if not len(items):
        raise HTTPException(status_code=404, detail="Department not found.")
    return items


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(db: db_dependency, item_request: ItemRequest):
    item_model = Items(**item_request.model_dump())
    db.add(item_model)
    db.commit()


@router.put("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_item(
    db: db_dependency, item_request: ItemRequest, product_id: int = Path(gt=0)
):
    item_model = db.query(Items).filter(Items.product_id == product_id).first()
    if item_model is None:
        raise HTTPException(status_code=404, detail="Item not found.")

    item_model.name = item_request.name
    item_model.product_id = item_request.product_id
    item_model.quantity = item_request.quantity
    item_model.href = item_request.href
    item_model.src = item_request.src
    item_model.alt = item_request.alt
    item_model.price = item_request.price

    db.add(item_model)
    db.commit()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(db: db_dependency, product_id: int):
    item_model = db.query(Items).filter(Items.product_id == product_id).first()
    if item_model is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    db.query(Items).filter(Items.product_id == product_id).first().delete()
