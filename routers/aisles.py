from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, noload, joinedload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Product, Aisle
from database import SessionLocal

# from .auth import get_current_user

router = APIRouter(
    #
    prefix="/aisles ",
    tags=["aisles"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class AisleRequest(BaseModel):
    name: str = Field()
    product_id: int = Field()
    rank: int = Field()
    department_id: int = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_items(db: db_dependency):
    return db.query(Aisle).all()


@router.get("/{aisle_id}", status_code=status.HTTP_200_OK)
async def read_aisle(
    db: db_dependency, aisle_id: int = Path(gt=0), with_products: bool = False
):
    if with_products:
        aisle_model = (
            db.query(Aisle)
            .options(joinedload("*"))
            .filter(Aisle.aisle_id == aisle_id)
            .first()
        )
    else:
        aisle_model = (
            db.query(Aisle)
            # .options(noload("*"))
            .filter(Aisle.aisle_id == aisle_id).first()
        )
    if aisle_model is None:
        raise HTTPException(status_code=404, detail="Aisle not found.")
    return aisle_model


@router.get("/by_department/{department_id}", status_code=status.HTTP_200_OK)
async def read_aisles_by_department(db: db_dependency, department_id: int = Path(gt=0)):
    aisles = db.query(Aisle).filter(Aisle.department_id == department_id).all()
    if not len(aisles):
        raise HTTPException(status_code=404, detail="Department not found.")
    return aisles


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_aisle(db: db_dependency, aisle_request: AisleRequest):
    aisle_model = Aisle(**aisle_request.model_dump())
    db.add(aisle_model)
    db.commit()


@router.put("/{aisle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_aisle(
    db: db_dependency, aisle_request: AisleRequest, aisle_id: int = Path(gt=0)
):
    aisle_model = db.query(Aisle).filter(Aisle.aisle_id == aisle_id).first()
    if aisle_model is None:
        raise HTTPException(status_code=404, detail="Aisle not found.")

    aisle_model.name = aisle_request.name
    aisle_model.aisle_id = aisle_request.aisle_id
    aisle_model.rank = aisle_request.rank
    aisle_model.price = aisle_request.price
    aisle_model.department_id = aisle_request.department_id

    db.add(aisle_model)
    db.commit()


@router.delete("/{aisle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aisle(db: db_dependency, aisle_id: int):
    aisle_model = db.query(Aisle).filter(Aisle.aisle_id == aisle_id).first()
    if aisle_model is None:
        raise HTTPException(status_code=404, detail="Aisle not found.")
    db.query(Aisle).filter(Aisle.aisle_id == aisle_id).first().delete()
