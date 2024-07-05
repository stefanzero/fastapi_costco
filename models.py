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
from sqlalchemy.orm import relationship

from database import Base


@enum.unique
class SectionType(str, enum.Enum):
    featured_products = "Featured Products"
    related_items = "Related Items"
    often_bought_with = "Often Bought With"


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    rank = Column(Integer)
    aisles = relationship("Aisle")

    def __repr__(self):
        return f"Department: {self.name}, department_id: {self.department_id}"

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
    department_id = Column(
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

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    rank = Column(Integer)
    product_id = Column(Integer, unique=True)
    size = Column(String)
    src = Column(String)
    alt = Column(String)
    price = Column(String)
    affix = Column(String)
    price_per = Column(String)
    aisle_id = Column(
        "aisle_id", Integer(), ForeignKey("aisles.aisle_id"), nullable=False
    )
    aisle = relationship(Aisle, back_populates="products")
    featured_products = relationship(
        "Section",
        primaryjoin=f"and_(\
                Section.parent_product_id == Product.product_id,\
                Section.section_type == 'featured_products',\
            )",
    )
    related_items = relationship(
        "Section",
        primaryjoin=f"and_(\
                Section.parent_product_id == Product.product_id,\
                Section.section_type == 'related_items',\
            )",
    )
    often_bought_with = relationship(
        "Section",
        primaryjoin=f"and_(\
                Section.parent_product_id == Product.product_id,\
                Section.section_type == 'often_bought_with',\
            )",
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
    parent = relationship(Product, primaryjoin=Product.product_id == parent_product_id)
    child = relationship(Product, primaryjoin=Product.product_id == child_product_id)
