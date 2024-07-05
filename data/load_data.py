import json
import os
import re

from box import Box

"""
https://pypi.org/project/python-box/
Box is a subclass of dict which overrides some base functionality 
to make sure everything stored in the dict can be accessed as an 
attribute or key value.
"""
from database import Session
from models import Aisle, Department, Product, Section, SectionType

root_path = os.path.dirname(__file__)

data_cache = {}

""" 
These data files were "scraped" from the Instacart web site using
- selenium webdriver
- BeautifulSoup HTML parser
"""
DATA_FILES = Box(
    {
        #
        costco: "costco.json",
        product_details: "product_details.json",
    }
)
"""
costco.json contains data for
- departments 
- aisles
- products

product_details.json contains data for
- product.alt (for image tag)
- product.price_per
- product.sections
  - featured_products
  - related_items
  - often_bought_with
"""


def get_costco() -> Box:
    if "costco" in data_cache:
        return data_cache["costco"]
    file_name = os.path.join(root_path, "costco.json")
    with open(file_name) as file:
        file_contents = file.read()
        costco = json.loads(file_contents)
    data_cache["costco"] = Box(costco)
    return data_cache["costco"]


def get_departments_with_rank() -> Box:
    if "departments_with_rank" in data_cache:
        return data_cache["departments_with_rank"]
    costco = get_costco()
    departments = costco.departments
    for rank, department_id in enumerate(costco.order):
        department = departments[str(department_id)]
        department.rank = rank
    department_list = [departments[str(id)] for id in costco.order]
    data_cache["departments_with_rank"] = department_list
    return data_cache["departments_with_rank"]


def get_aisles_with_rank() -> dict[str, Box]:
    departments = get_departments_with_rank()
    aisles_map = {}
    for department in departments:
        department_id = department.id
        for rank, aisle_id in enumerate(department.order):
            aisle = department.aisles[str(aisle_id)]
            aisle.department_id = department_id
            aisle.rank = rank
            aisles_map[str(aisle_id)] = aisle
    data_cache["aisles_with_rank"] = aisles_map
    return aisles_map


def get_products_details() -> Box:
    if "products_details" in data_cache:
        return data_cache["products_details"]
    file_name = os.path.join(root_path, "products_details.json")
    with open(file_name) as file:
        file_contents = file.read()
        product_details = json.loads(file_contents)
    data_cache["products_details"] = Box(product_details)
    return data_cache["products_details"]


def get_products_with_rank() -> dict[str, Box]:
    if "items_with_rank" in data_cache:
        return data_cache["items_with_rank"]
    aisles = get_aisles_with_rank()
    products_map = {}
    for aisle in aisles.values():
        aisle_id = aisle.id
        for rank, product_id in enumerate(aisle.order):
            product = aisle.products[str(product_id)]
            product.rank = rank
            product.aisle_id = aisle_id
            products_map[str(product_id)] = product

    data_cache["products_with_rank"] = products_map
    return data_cache["products_with_rank"]


def get_aisle_from_breadcrumbs(breadcrumbs: list[dict]):
    if len(breadcrumbs) < 2:
        return None
    href1 = breadcrumbs[1]["href"]
    match = re.search(r"\d+$", href1)
    if match:
        return match[0]


def insert_department(department: Box) -> None:
    values = {
        "department_id": department.id,
        "name": department.name,
        "rank": department.rank,
    }
    with Session() as db:
        try:
            obj = Department(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def insert_aisle(aisle: Box) -> None:
    values = {
        "aisle_id": aisle.id,
        "name": aisle.name,
        "department_id": aisle.department_id,
        "rank": aisle.rank,
    }
    with Session() as db:
        try:
            obj = Aisle(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def insert_product(product: Box) -> None:
    print(product.name)
    values = {
        "affix": product.affix,
        "product_id": product.product_id,
        "rank": product.rank,
        "name": product.name,
        "price": product.price,
        "src": product.src,
        "size": product.size,
        "aisle_id": product.aisle_id,
    }
    with Session() as db:
        try:
            obj = Product(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def update_product_details(product_details: Box) -> None:
    with Session() as db:
        try:
            product_id = product_details.product_id
            obj = db.query(Product).filter(Product.product_id == product_id).first()
            if not obj:
                print(f"Could not find product {product_id}")
                return
            obj.alt = product_details.alt
            obj.price_per = product_details.price
            db.add(obj)
            db.commit()
            print(obj.product_id)
        except Exception as e:
            print(e)


def insert_sections(product: Box):
    for section in product.sections:
        section_name = section.name
        if section_name not in SectionType:
            print(
                f"Invalid section name {section_name} for product {product.product_id}"
            )
            continue
        if section.products:
            for section_product in section.products:
                if not section_product.product_id:
                    continue
                values = {
                    "section_type": SectionType(section.name),
                    "parent_product_id": product.product_id,
                    "child_product_id": section_product.product_id,
                }
                # print(section_dict["name"], item_dict["product_id"], section_item["product_id"])
                with Session() as db:
                    try:
                        obj = Section(**values)
                        db.add(obj)
                        db.commit()
                    except Exception as e:
                        # pass
                        print(e)


def insert_all_departments() -> None:
    departments = get_departments_with_rank()
    for department in departments:
        # print(department["name"])
        print(department.name)
        insert_department(department=department)


def insert_all_aisles_with_rank() -> None:
    aisles = get_aisles_with_rank()
    for aisle in aisles.values():
        print(aisle["name"])
        insert_aisle(aisle=aisle)


def insert_all_products() -> None:
    products = get_products_with_rank()
    for product in products.values():
        print(product["name"])
        insert_product(product=product)


def update_all_product_details() -> None:
    product_details = get_products_details()
    for product_detail in product_details.values():
        update_product_details(product_detail)


def insert_all_sections() -> None:
    products = get_products_details()
    for product in products.values():
        # print(item["name"])
        insert_sections(product=product)


def insert_section_by_index(index: int) -> None:
    products = get_products_details()
    keys = list(products.keys())
    product = products[keys[index]]
    insert_sections(product=product)
