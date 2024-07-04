from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Aisle, Department
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


class DepartmentRequest(BaseModel):
    name: str = Field()
    product_id: int = Field()
    rank: int = Field()
    department_id: int = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_items(db: db_dependency):
    return db.query(Department).all()


@router.get("/{department_id}", status_code=status.HTTP_200_OK)
async def read_department(
    db: db_dependency,
    department_id: int = Path(gt=0),
    with_aisles: bool = False,
    with_products: bool = False,
):
    if with_aisles and with_products:
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
            # .options(noload("*"))
            .filter(Department.department_id == department_id).first()
        )
    if department_model is None:
        raise HTTPException(status_code=404, detail="Department not found.")
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
    db.query(Department).filter(
        Department.department_id == department_id
    ).first().delete()
