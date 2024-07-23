from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, noload, joinedload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from src.models import Product, Aisle, Department
from src.database import SessionLocal, get_db

# from .auth import get_current_user

router = APIRouter(
    #
    prefix="/aisles",
    tags=["aisles"],
)


db_dependency = Annotated[Session, Depends(get_db)]


def add_href(models: list[BaseModel]) -> None:
    for model in models:
        model.href


class AisleRequest(BaseModel):
    name: str = Field()
    aisle_id: int = Field()
    rank: int = Field()
    department_id: int = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_aisles(db: db_dependency):
    aisles = db.query(Aisle).all()
    add_href(aisles)
    return aisles


@router.get("/{aisle_id}", status_code=status.HTTP_200_OK)
async def read_aisle(
    db: db_dependency, aisle_id: int = Path(gt=0), with_products: bool = False
):
    if with_products:
        aisle_model = (
            db.query(Aisle)
            .options(noload(Aisle.department))
            .options(joinedload(Aisle.products).noload(Product.featured_products))
            .options(joinedload(Aisle.products).noload(Product.related_items))
            .options(joinedload(Aisle.products).noload(Product.often_bought_with))
            .filter(Aisle.aisle_id == aisle_id)
            .first()
        )
        for product in aisle_model.products:
            product.href
    else:
        aisle_model = (
            db.query(Aisle)
            .options(noload("*"))
            .filter(Aisle.aisle_id == aisle_id)
            .first()
        )
        if hasattr(aisle_model, "products"):
            delattr(aisle_model, "products")
    if aisle_model is None:
        raise HTTPException(status_code=404, detail="Aisle not found.")
    aisle_model.href
    # TODO: remove join from load
    delattr(aisle_model, "department")
    if hasattr(aisle_model, "products"):
        products: list[Product] = aisle_model.products
        for product in products:
            product.remove_section_relationships()
    return aisle_model


@router.get("/by_department/{department_id}", status_code=status.HTTP_200_OK)
async def read_aisles_by_department(db: db_dependency, department_id: int = Path(gt=0)):
    aisles = (
        db.query(Aisle)
        .options(noload("*"))
        .filter(Aisle.department_id == department_id)
        .all()
    )
    if not len(aisles):
        raise HTTPException(status_code=404, detail="Department not found.")
    for aisle in aisles:
        delattr(aisle, "department")
        delattr(aisle, "products")
    add_href(aisles)
    return aisles


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_aisle(db: db_dependency, aisle_request: AisleRequest):
    aisle_model = Aisle(**aisle_request.model_dump())
    aisle_id = aisle_model.aisle_id
    aisle = db.query(Aisle).filter(Aisle.aisle_id == aisle_id).first()
    if aisle:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot create aisle.  Aisle already exists with aisle_id {aisle_id}",
        )
    department_id = aisle_model.department_id
    department = (
        db.query(Department).filter(Department.department_id == department_id).first()
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot create aisle.  Department not found with department_id {department_id}",
        )
    db.add(aisle_model)
    db.commit()
    db.refresh(aisle_model)


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
    aisle_model.department_id = aisle_request.department_id
    department_id = aisle_model.department_id
    department = (
        db.query(Department).filter(Department.department_id == department_id).first()
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot update aisle.  Department not found with department_id {department_id}",
        )
    db.add(aisle_model)
    db.commit()
    db.refresh(aisle_model)


@router.delete("/{aisle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aisle(db: db_dependency, aisle_id: int):
    aisle_model = db.query(Aisle).filter(Aisle.aisle_id == aisle_id).first()
    if aisle_model is None:
        raise HTTPException(status_code=404, detail="Aisle not found.")
    db.query(Aisle).filter(Aisle.aisle_id == aisle_id).delete()
    db.commit()
