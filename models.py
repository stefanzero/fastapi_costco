import enum
from functools import cached_property
from pydantic import computed_field
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
)

from database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    rank = Column(Integer)

    @computed_field
    @cached_property
    def href(self):
        return f"costco/departments/{self.department_id}"


class Aisle(Base):
    __tablename__ = "aisles"

    id = Column(Integer, primary_key=True, index=True)
    aisle_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    rank = Column(Integer)
    # department: Department = ForeignKey()
    department_id = Column(
        "department_id",
        Integer(),
        ForeignKey("departments.department_id"),
        nullable=False,
    )

    @computed_field
    @cached_property
    def href(self):
        return f"costco/departments/{self.department_id}/aisles/{self.aisle_id}"


class Product(Base):
    """
    "product_id": "15218037",
    "name": "Organic Blackberries, 12 oz",
    "price": "$8.70\u00a0/each",
    "quantity": "12 oz\u00a0",
    "src": "https://d2d8wwwkmhfcva.cloudfront.net/1200x/filters:fill(FFF,true):format(jpg)/d2lnr5mha7bycj.cloudfront.net/product-image/file/large_91f25f39-b830-44a0-9224-f271c484af59.jpeg",
    "alt": "image of Organic Blackberries, 12 oz",
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    rank = Column(Integer)
    product_id = Column(Integer, unique=True)
    # quantity = Column(String)
    size = Column(String)
    src = Column(String)
    alt = Column(String)
    price = Column(String)
    affix = Column(String)
    price_per = Column(String)
    aisle_id = Column(
        "aisle_id", Integer(), ForeignKey("aisles.aisle_id"), nullable=False
    )

    @computed_field
    @cached_property
    def href(self):
        return f"/store/items/item{self.product_id}"


class SectionType(str, enum.Enum):
    featured_products = "Featured Products"
    related_items = "Related Items"
    often_bought_with = "Often Bought With"


class Section(Base):
    __tablename__ = "sections"

    # id = Column(Integer, primary_key=True, index=True)
    section_type = Column("section_type", Enum(SectionType), primary_key=True)
    parent_product_id = Column(
        "parent_product_id",
        Integer(),
        ForeignKey("products.product_id"),
        nullable=False,
        primary_key=True,
    )
    child_product_id = Column(
        "child_product_id",
        Integer(),
        ForeignKey("products.product_id"),
        nullable=False,
        primary_key=True,
    )
    # __table_args__ = (
    #     UniqueConstraint(
    #         "section_type", "parent_item_id", name="section_type_parent_unique"
    #     ),
    # )


# class BreadCrumbs(Base):
#     __tablename__ = "breadcrumbs"

"""
Section

section_type enum
parent_item_id
child_item_id

section_type, parent_item_id index
"""
