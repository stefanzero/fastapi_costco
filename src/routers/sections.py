from typing import Annotated, Self, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from box import Box

# from sqlalchemy import Enum
from sqlalchemy.orm import Session, noload, joinedload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from src.models import SectionType, Section, Product
from src.database import get_db

# from .auth import get_current_user

router = APIRouter(
    #
    prefix="/sections",
    tags=["sections"],
)


db_dependency = Annotated[Session, Depends(get_db)]


class SectionRequest(BaseModel):
    """
    SectionObject must have parent and child that exist,
    and they must be different
    """

    section_type: SectionType = Field()
    parent_product_id: int = Field()
    child_product_id: int = Field()

    # @field_validator("parent_product_id")
    # @classmethod
    # def check_parent_id(
    #     cls, parent_product_id: int, db: Session = Depends(get_db)
    # ) -> int:
    #     # with next(get_db()) as db:
    #     i = 1
    #     product_model = (
    #         db.query(Product).filter(Product.product_id == parent_product_id).first()
    #     )
    #     if product_model is None:
    #         raise ValueError(f"Parent product {parent_product_id} not found.")
    #     return parent_product_id

    # @field_validator("child_product_id")
    # @classmethod
    # def check_child_id(cls, child_product_id: int) -> int:
    #     with next(get_db()) as db:
    #         product_model = (
    #             db.query(Product).filter(Product.product_id == child_product_id).first()
    #         )
    #         if product_model is None:
    #             raise ValueError(f"Child product {child_product_id} not found.")
    #     return child_product_id

    @model_validator(mode="after")
    def check_parent_child(self) -> Self:
        if self.parent_product_id == self.child_product_id:
            raise ValueError("Parent and Child must be different products")
        return self


def ensure_product_exists(product_id: int, db: Session):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot section entry. Product does not exist with product_id {product_id}",
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def read_sections(db: db_dependency):
    sections = (
        #
        db.query(Section)
        .order_by(Section.parent_product_id, Section.section_type)
        .options(noload("*"))
        .all()
    )
    for section in sections:
        if hasattr(section, "parent"):
            delattr(section, "parent")
        if hasattr(section, "child"):
            delattr(section, "child")
    return sections


"""
"parent_product_id": 10075153,
"child_product_id": 10076972,
"section_type": "Featured Products"
"""


@router.get(
    "/{section_type}/{parent_product_id}/{child_product_id}",
    status_code=status.HTTP_200_OK,
)
async def read_section(
    db: db_dependency,
    section_type: SectionType,
    # section_type: Literal["featured_products", "often_bought_with", "related_items"],
    parent_product_id: int,
    child_product_id: int,
):
    section_model = (
        db.query(Section)
        # .options(noload("*"))
        .filter(Section.parent_product_id == parent_product_id)
        .filter(Section.child_product_id == child_product_id)
        .filter(Section.section_type == section_type)
        .first()
    )
    if section_model is None:
        raise HTTPException(status_code=404, detail="Section not found.")
    return section_model


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_section(db: db_dependency, section_request: SectionRequest):
    ensure_product_exists(product_id=section_request.parent_product_id, db=db)
    ensure_product_exists(product_id=section_request.child_product_id, db=db)
    section_model = Section(**section_request.model_dump())
    db.add(section_model)
    db.commit()


# @router.put("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_section(
#     db: db_dependency,
#     section_request: SectionRequest,
#     section_id: int = Path(gt=0),
# ):
#     section_model = db.query(Section).filter(Section.section_id == section_id).first()
#     if section_model is None:
#         raise HTTPException(status_code=404, detail="Section not found.")

#     section_model.name = section_request.name
#     section_model.section_id = section_request.section_id
#     section_model.rank = section_request.rank

#     db.add(section_model)
#     db.commit()


@router.delete(
    "/{section_type}/{parent_product_id}/{child_product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_section(
    db: db_dependency,
    section_type: SectionType,
    parent_product_id: int,
    child_product_id: int,
):
    section_model = (
        db.query(Section)
        # .options(noload("*"))
        .filter(Section.parent_product_id == parent_product_id)
        .filter(Section.child_product_id == child_product_id)
        .filter(Section.section_type == section_type)
        .first()
    )
    if section_model is None:
        raise HTTPException(status_code=404, detail="Section not found.")
    (
        db.query(Section)
        .filter(Section.parent_product_id == parent_product_id)
        .filter(Section.child_product_id == child_product_id)
        .filter(Section.section_type == section_type)
        .delete()
    )
    db.commit()


@router.get(
    "/by_parent_product_id/{parent_product_id}",
    status_code=status.HTTP_200_OK,
)
async def read_sections_by_product_id(
    db: db_dependency,
    parent_product_id: int,
):
    section_models = (
        db.query(Section)
        .options(joinedload(Section.child))
        .filter(Section.parent_product_id == parent_product_id)
        .all()
    )
    if section_models is None:
        raise HTTPException(status_code=404, detail="Section not found.")
    sections = {}
    for section_type in SectionType._member_names_:
        sections[section_type] = []
    for model in section_models:
        if model.child:
            section = SectionType(model.section_type).name
            sections[section].append(model.child)
    return sections
