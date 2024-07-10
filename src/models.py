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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from box import BoxList
from typing import Self

from .database import Base


@enum.unique
class SectionType(str, enum.Enum):
    featured_products = "Featured Products"
    related_items = "Related Items"
    often_bought_with = "Often Bought With"


class Department(Base):
    __tablename__ = "departments"

    # id = Column(Integer, primary_key=True, index=True)
    # department_id = Column(Integer, unique=True, index=True)
    # name = Column(String)
    # rank = Column(Integer)
    # aisles = relationship("Aisle", back_populates="department")
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    rank: Mapped[int] = mapped_column()
    aisles = relationship("Aisle", back_populates="department")

    def __repr__(self):
        return f"Department: {self.name}, department_id: {self.department_id}"

    @computed_field
    @cached_property
    def href(self):
        return f"costco/departments/{self.department_id}"


class Aisle(Base):
    __tablename__ = "aisles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aisle_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    rank: Mapped[str] = mapped_column(Integer)
    department_id: Mapped[int] = mapped_column(
        "department_id",
        Integer(),
        ForeignKey("departments.department_id"),
        nullable=False,
    )
    department = relationship(Department, back_populates="aisles")
    products = relationship("Product")

    def __repr__(self):
        return f"Aisle: {self.name}, aisle_id: {self.aisle_id}"

    @computed_field
    @cached_property
    def href(self):
        return f"costco/departments/{self.department_id}/aisles/{self.aisle_id}"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    rank: Mapped[int] = mapped_column()
    product_id: Mapped[int] = mapped_column(unique=True)
    size: Mapped[str] = mapped_column()
    src: Mapped[str] = mapped_column()
    alt: Mapped[str] = mapped_column()
    price: Mapped[str] = mapped_column()
    affix: Mapped[str] = mapped_column()
    price_per: Mapped[str] = mapped_column()
    aisle_id: Mapped[str] = mapped_column(
        "aisle_id", Integer(), ForeignKey("aisles.aisle_id"), nullable=False
    )
    aisle = relationship(Aisle, back_populates="products")
    featured_products = relationship(
        "Section",
        primaryjoin=f"and_(\
                Section.parent_product_id == Product.product_id,\
                Section.section_type == 'featured_products',\
            )",
        viewonly=True,
    )
    related_items = relationship(
        "Section",
        primaryjoin=f"and_(\
                Section.parent_product_id == Product.product_id,\
                Section.section_type == 'related_items',\
            )",
        viewonly=True,
    )
    often_bought_with = relationship(
        "Section",
        primaryjoin=f"and_(\
                Section.parent_product_id == Product.product_id,\
                Section.section_type == 'often_bought_with',\
            )",
        viewonly=True,
    )

    def __repr__(self):
        return f"Product: {self.name}, product_id: {self.product_id}"

    @computed_field
    @cached_property
    def href(self):
        return f"/store/items/item{self.product_id}"

    @computed_field
    @cached_property
    def sections(self):
        """
        Create a "sections" dictionary
           key = SectionType
           value = list of products

        Use "child" relationship in Section to hydrate the Product

        Note: makes a separate query for every child
        """
        return {
            "featured_products": [
                x.child for x in self.featured_products if x.child is not None
            ],
            "related_items": [
                x.child for x in self.related_items if x.child is not None
            ],
            "often_bought_with": [
                x.child for x in self.often_bought_with if x.child is not None
            ],
        }

    def add_sections(self) -> None:
        """
        Cache the sections dictionary and remove the raw Section relationship
        from the object
        """
        self.sections
        self.remove_section_relationships()

    def remove_section_relationships(self) -> None:
        for member in SectionType:
            name = member.name
            if name in self.__dict__:
                self.__dict__.pop(member.name)


class Section(Base):
    __tablename__ = "sections"

    # id = Column(Integer, primary_key=True, index=True)
    section_type: Mapped[SectionType] = mapped_column(
        "section_type", Enum(SectionType), primary_key=True
    )
    parent_product_id: Mapped[int] = mapped_column(
        "parent_product_id",
        Integer(),
        ForeignKey("products.product_id"),
        nullable=False,
        primary_key=True,
    )
    child_product_id: Mapped[int] = mapped_column(
        "child_product_id",
        Integer(),
        ForeignKey("products.product_id"),
        nullable=False,
        primary_key=True,
    )
    parent = relationship(Product, primaryjoin=Product.product_id == parent_product_id)
    child = relationship(Product, primaryjoin=Product.product_id == child_product_id)
