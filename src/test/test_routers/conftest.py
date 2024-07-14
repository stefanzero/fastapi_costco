import pytest
import json
from typing import Generator
from sqlalchemy.orm.session import Session
from sqlalchemy import inspect
from box import Box, BoxList

from src.models import Department, Aisle, Product, Section, SectionType
from src.database import Base

department_data = Box({"name": "Electronics", "rank": 1, "department_id": 999})


def to_dict(obj):
    # return json.loads(json.dumps(obj, default=lambda o: o.__dict__))
    obj_dict = json.loads(json.dumps(obj, default=lambda o: o.__dict__))
    return obj_dict


# vars(row).keys().filter(lambda x: not x.startswith('_'))
def row_to_dict(row):
    dict_ = {}
    i = inspect(row)
    # keys = row.__mapper__.c.keys()
    # keys = vars(row).keys().filter(lambda x: not x.startswith("_"))
    keys = [key for key in vars(row).keys() if not key.startswith("_")]
    for key in keys:
        value = getattr(row, key)
        dict_[key] = value
    # for key in i.mapper.relationships.keys():
    #     value = getattr(row, key)
    #     if isinstance(value, Base):
    #         value = row_to_dict(value)
    #         dict_[key] = value
    #     elif isinstance(value, list):
    #         values = []
    #         for v in value:
    #             v_dict = row_to_dict(v)
    #             values.append(v_dict)
    #         dict_[key] = values
    return dict_


test_data = Box(
    {
        "departments": {
            "1": {
                "department_id": 1,
                "name": "Wines",
                "rank": 1,
                "aisles": {
                    "101": {
                        "aisle_id": 101,
                        "name": "Red Wines",
                        "rank": 1,
                        "products": {
                            "1001": {
                                "product_id": 1001,
                                "name": "Louis M. Martini Cabernet Sauvignon, Sonoma County",
                                "size": "750ml",
                                "src": "https://www.instacart.com/assets/domains/product-image/file/large_88f792c4-8e32-4218-a04b-b562c8e40132.jpeg",
                                "alt": "image of Louis M. Martini Cabernet Sauvignon",
                                "price": "$16.69",
                                "affix": "each",
                                "price_per": "$16.69/each",
                                "rank": 1,
                                "sections": {
                                    "Related Items": [{"product_id": 1002}],
                                    "Featured Products": [{"product_id": 2002}],
                                    "Often Bought With": [{"product_id": 2001}],
                                },
                            },
                            "1002": {
                                "product_id": 1002,
                                "name": "Kirkland Signature Chianti Classico Riserva, Italy",
                                "size": "750ml",
                                "src": "https://www.instacart.com/assets/domains/product-image/file/large_c32f05f7-145f-45b7-9407-0e354f50f864.jpeg",
                                "alt": "image of Kirkland Signature Chianti Classico Riserva",
                                "price": "$10.89",
                                "affix": "each",
                                "price_per": "$10.89/each",
                                "rank": 2,
                                "sections": {
                                    "Related Items": [{"product_id": 1002}],
                                    "Featured Products": [{"product_id": 2002}],
                                    "Often Bought With": [{"product_id": 2001}],
                                },
                            },
                        },
                    },
                    "102": {
                        "aisle_id": 102,
                        "name": "White Wines",
                        "rank": 2,
                        "products": {
                            "2001": {
                                "product_id": 2001,
                                "name": "Charles Krug, Sauvignon Blanc, Napa Valley",
                                "size": "750 ml",
                                "src": "https://d2lnr5mha7bycj.cloudfront.net/product-image/file/large_35216ef9-8337-409c-8bdc-6061f1656413.jpeg",
                                "alt": "image of Charles Krug, Sauvignon Blanc",
                                "price": "$19.19",
                                "affix": "each",
                                "price_per": "$19.19/each",
                                "rank": 1,
                                "sections": {
                                    "Related Items": [{"product_id": 1002}],
                                    "Featured Products": [{"product_id": 2002}],
                                    "Often Bought With": [{"product_id": 2001}],
                                },
                            },
                            "2002": {
                                "product_id": 2002,
                                "name": "Kendall-Jackson Vintner's Reserve Chardonnay White Wine",
                                "size": "750 ml",
                                "src": "https://www.instacart.com/assets/domains/product-image/file/large_b9869d0b-b3af-4f9e-88f0-2fbf3a888239.jpeg",
                                "alt": "image of Kendall-Jackson Vintner's Reserve Chardonnay White Wine",
                                "price": "$13.59",
                                "affix": "each",
                                "price_per": "$13.59/each",
                                "rank": 2,
                                "sections": {
                                    "Related Items": [{"product_id": 1002}],
                                    "Featured Products": [{"product_id": 2002}],
                                    "Often Bought With": [{"product_id": 2001}],
                                },
                            },
                        },
                    },
                },
            }
        }
    }
)


@pytest.fixture
def test_department(db: Session) -> Generator[Department, None, None]:
    department = Department(**department_data)
    db.add(department)
    db.commit()
    yield department
    tear_down_department(db)


def tear_down_department(db: Session):
    db.query(Department).delete()
    db.commit()
    # test
    sections = db.query(Section).all()
    print(len(sections))


@pytest.fixture
def test_departments(db: Session) -> Generator[BoxList[Department], None, None]:
    departments = BoxList()
    for department in test_data.departments.values():
        department_model = Department(
            department_id=department.department_id,
            name=department.name,
            rank=department.rank,
        )
        db.add(department_model)
        db.commit()
        department_model.href
        department_box = Box(row_to_dict(department_model))
        department_box.aisles = BoxList()
        for aisle in department.aisles.values():
            aisle_model = Aisle(
                aisle_id=aisle.aisle_id,
                name=aisle.name,
                rank=aisle.rank,
                department_id=department.department_id,
            )
            db.add(aisle_model)
            db.commit()
            aisle_model.href
            aisle_box = Box(row_to_dict(aisle_model))
            aisle_box.products = BoxList()
            for product in aisle.products.values():
                product_model = Product(
                    product_id=product.product_id,
                    name=product.name,
                    size=product.size,
                    src=product.src,
                    alt=product.alt,
                    rank=product.rank,
                    price=product.price,
                    price_per=product.price_per,
                    affix=product.affix,
                    aisle_id=aisle.aisle_id,
                )
                db.add(product_model)
                db.commit()
                product_model.href
                product_box = Box(row_to_dict(product_model))
                aisle_box.products.append(product_box)
            department_box.aisles.append(aisle_box)
        departments.append(department_box)
    # all products must be added before sections can reference them
    # the sections should only be returned from creating a product fixture
    # for department in test_data.departments.values():
    #     for aisle in department.aisles.values():
    #         for product in aisle.products.values():
    #             for section, child_products in product.sections.items():
    #                 for child_product in child_products:
    #                     section_model = Section(
    #                         section_type=SectionType(section),
    #                         parent_product_id=product.product_id,
    #                         child_product_id=child_product.product_id,
    #                     )
    #                     db.add(section_model)
    #                     db.commit()
    # reload the data
    # for department in test_data.departments.values():
    #     department_model = (
    #         db.query(Department)
    #         .filter(Department.department_id == department.department_id)
    #         .first()
    #     )
    #     departments.append(Box(row_to_dict(department_model)))

    yield departments
    tear_down_department(db)


@pytest.fixture(scope="function")
def test_product(db: Session) -> Generator[Box[Product], None, None]:
    department_ids = sorted(test_data.departments.keys())
    department = test_data.departments[department_ids[0]]
    aisle_ids = sorted(department.aisles.keys())
    aisle = department.aisles[aisle_ids[0]]
    product_ids = sorted(aisle.products.keys())
    product = aisle.products[product_ids[0]]
    product.aisle_id = aisle.aisle_id
    return add_product(product, db)


def add_product(product: dict, db: Session) -> Box:
    product_model = Product(
        product_id=product.product_id,
        name=product.name,
        size=product.size,
        src=product.src,
        alt=product.alt,
        rank=product.rank,
        price=product.price,
        price_per=product.price_per,
        affix=product.affix,
        aisle_id=product.aisle_id,
    )
    db.add(product_model)
    db.commit()
    product_model.href
    product_box = Box(row_to_dict(product_model))
    return product_box
