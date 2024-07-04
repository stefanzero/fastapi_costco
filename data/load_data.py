import json
import os
import re
from sqlalchemy import select

# from functools import reduce
from box import Box

from database import Session
from models import Aisle, Department, Product, Section, SectionType

root_path = os.path.dirname(__file__)

data_cache = {}


def get_store():
    if "store" in data_cache:
        return data_cache["store"]
    file_name = os.path.join(root_path, "store.json")
    with open(file_name) as file:
        file_contents = file.read()
        store = json.loads(file_contents)
    data_cache["store"] = Box(store)
    return data_cache["store"]


def get_departments_with_rank():
    if "departments_with_rank" in data_cache:
        return data_cache["departments_with_rank"]
    store = get_store()
    departments = store.departments
    for rank, department_id in enumerate(store.order):
        department = departments[str(department_id)]
        department.rank = rank
    department_list = [departments[str(id)] for id in store.order]
    data_cache["departments_with_rank"] = department_list
    return data_cache["departments_with_rank"]


def get_departments():
    if "departments" in data_cache:
        return data_cache["departments"]
    file_name = os.path.join(root_path, "departments.json")
    with open(file_name) as file:
        file_contents = file.read()
        departments = json.loads(file_contents)
    data_cache["departments"] = departments
    return data_cache["departments"]


# def get_aisles():
#     if "aisles" in data_cache:
#         return data_cache["aisles"]
#     departments = get_departments()
#     aisles_map = {}
#     for department_id, department in departments.items():
#         aisles = department["aisles"]
#         for aisle_id, aisle in aisles.items():
#             aisle["department_id"] = department_id
#             aisles_map[aisle_id] = aisle
#     data_cache["aisles"] = aisles_map
#     return aisles_map


def get_aisles_with_rank():
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


# this will still be needed to load "alt", "price_per" and "quantity"
def get_products_details():
    if "products_details" in data_cache:
        return data_cache["products_details"]
    file_name = os.path.join(root_path, "products_details.json")
    with open(file_name) as file:
        file_contents = file.read()
        product_details = json.loads(file_contents)
    data_cache["products_details"] = Box(product_details)
    return data_cache["products_details"]


def get_products_with_rank():
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


def insert_department(department: Box):
    # department = Box(department_dict)
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


def insert_aisle(aisle: Box):
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


# def insert_item(item_dict):
#     item = Box(item_dict)
#     aisle_id = get_aisle_from_breadcrumbs(item.breadcrumbs)
#     if not aisle_id:
#         print(f"item {item.product_id} has no aisle")
#         return
#     print(item.name)
#     values = {
#         "product_id": item.product_id,
#         "name": item.name,
#         "price": item.price,
#         "src": item.src,
#         "alt": item.alt,
#         "quantity": item.quantity,
#         "aisle_id": aisle_id,
#     }
#     with Session() as db:
#         try:
#             obj = Items(**values)
#             db.add(obj)
#             db.commit()
#         except Exception as e:
#             print(e)


def insert_product(product: Box):
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


def update_product_details(product_details: Box):
    with Session() as db:
        try:
            product_id = product_details.product_id
            obj = db.query(Product).filter(Product.product_id == product_id).first()
            if not obj:
                print(f"Could not find product {product_id}")
                return
            obj.alt = product_details.alt
            # obj.quantity = product_details.quantity
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


def insert_all_departments():
    departments = get_departments_with_rank()
    for department in departments:
        # print(department["name"])
        print(department.name)
        insert_department(department=department)


def insert_all_aisles_with_rank():
    aisles = get_aisles_with_rank()
    for aisle in aisles.values():
        print(aisle["name"])
        insert_aisle(aisle=aisle)


def insert_all_products():
    products = get_products_with_rank()
    for product in products.values():
        print(product["name"])
        insert_product(product=product)


def update_all_product_details():
    product_details = get_products_details()
    for product_detail in product_details.values():
        update_product_details(product_detail)


def insert_all_sections():
    products = get_products_details()
    for product in products.values():
        # print(item["name"])
        insert_sections(product=product)


def insert_section_by_index(index: int):
    products = get_products_details()
    keys = list(products.keys())
    product = products[keys[index]]
    insert_sections(product=product)
