from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload, noload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Aisle, Department, Product
from database import SessionLocal

# from .auth import get_current_user

router = APIRouter(
    #
    prefix="/departments",
    tags=["departments"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def add_href(models: list[BaseModel]) -> None:
    for model in models:
        model.href


class DepartmentRequest(BaseModel):
    name: str = Field()
    product_id: int = Field()
    rank: int = Field()
    department_id: int = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_departments(db: db_dependency):
    departments = db.query(Department).all()
    add_href(departments)
    return departments


@router.get("/{department_id}", status_code=status.HTTP_200_OK)
async def read_department(
    db: db_dependency,
    department_id: int = Path(gt=0),
    with_aisles: bool = False,
    with_aisles_and_products: bool = False,
):
    if with_aisles_and_products:
        department_model = (
            db.query(Department)
            .options(joinedload("*"))
            .filter(Department.department_id == department_id)
            .first()
        )
    elif with_aisles:
        department_model = (
            db.query(Department)
            .options(joinedload(Department.aisles))
            .filter(Department.department_id == department_id)
            .first()
        )
    else:
        department_model = (
            db.query(Department)
            .options(noload("*"))
            .filter(Department.department_id == department_id)
            .first()
        )
        if hasattr(department_model, "aisles"):
            delattr(department_model, "aisles")
    if department_model is None:
        raise HTTPException(status_code=404, detail="Department not found.")
    department_model.href
    if hasattr(department_model, "aisles"):
        aisles: list[Aisle] = department_model.aisles
        for aisle in aisles:
            aisle.href
            if hasattr(aisle, "products"):
                if not with_aisles_and_products:
                    delattr(aisle, "products")
                else:
                    products: list[Product] = aisle.products
                    for product in products:
                        product.href
                        product.remove_section_relationships()
    return department_model


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department(db: db_dependency, department_request: DepartmentRequest):
    department_model = Department(**department_request.model_dump())
    db.add(department_model)
    db.commit()


@router.put("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_department(
    db: db_dependency,
    department_request: DepartmentRequest,
    department_id: int = Path(gt=0),
):
    department_model = (
        db.query(Department).filter(Department.department_id == department_id).first()
    )
    if department_model is None:
        raise HTTPException(status_code=404, detail="Department not found.")

    department_model.name = department_request.name
    department_model.department_id = department_request.department_id
    department_model.rank = department_request.rank

    db.add(department_model)
    db.commit()


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(db: db_dependency, department_id: int):
    department_model = (
        db.query(Department).filter(Department.department_id == department_id).first()
    )
    if department_model is None:
        raise HTTPException(status_code=404, detail="Department not found.")
    db.query(Department).filter(Department.department_id == department_id).delete()
    db.commit()
