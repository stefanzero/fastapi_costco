import json
import os
import re

# from functools import reduce
from box import Box

from database import Session
from models import Aisles, Departments, Items, Sections, SectionType

root_path = os.path.dirname(__file__)

data_cache = {}


def get_departments():
    if "departments" in data_cache:
        return data_cache["departments"]
    file_name = os.path.join(root_path, "departments.json")
    with open(file_name) as file:
        file_contents = file.read()
        departments = json.loads(file_contents)
    data_cache["departments"] = departments
    return data_cache["departments"]


def get_aisles():
    if "aisles" in data_cache:
        return data_cache["aisles"]
    departments = get_departments()
    aisles_map = {}
    for department_id, department in departments.items():
        aisles = department["aisles"]
        for aisle_id, aisle in aisles.items():
            aisle["department_id"] = department_id
            aisles_map[aisle_id] = aisle
    data_cache["aisles"] = aisles_map
    return aisles_map


def get_items():
    if "items" in data_cache:
        return data_cache["items"]
    file_name = os.path.join(root_path, "items.json")
    with open(file_name) as file:
        file_contents = file.read()
        items = json.loads(file_contents)
    data_cache["items"] = items
    return data_cache["items"]


def get_aisle_from_breadcrumbs(breadcrumbs: list[dict]):
    if len(breadcrumbs) < 2:
        return None
    href1 = breadcrumbs[1]["href"]
    match = re.search(r"\d+$", href1)
    if match:
        return match[0]


def insert_department(department_dict: dict):
    department = Box(department_dict)
    values = {
        "department_id": department.id,
        "name": department.name,
    }
    with Session() as db:
        try:
            obj = Departments(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def insert_aisle(aisle_dict):
    aisle = Box(aisle_dict)
    values = {
        "aisle_id": aisle.id,
        "name": aisle.name,
        "department_id": aisle.department_id,
    }
    with Session() as db:
        try:
            obj = Aisles(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def insert_item(item_dict):
    item = Box(item_dict)
    aisle_id = get_aisle_from_breadcrumbs(item.breadcrumbs)
    if not aisle_id:
        print(f"item {item.product_id} has no aisle")
        return
    print(item.name)
    values = {
        "product_id": item.product_id,
        "name": item.name,
        "price": item.price,
        "src": item.src,
        "alt": item.alt,
        "quantity": item.quantity,
        "aisle_id": aisle_id,
    }
    with Session() as db:
        try:
            obj = Items(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def insert_sections(item_dict):
    for section_dict in item_dict["sections"]:
        section_name = section_dict["name"]
        if section_name not in SectionType:
            print(f"Invalid section name {section_name} for product {item_dict["product_id"]}")
            continue
        if "items" in section_dict:
            for section_item in section_dict["items"]:
                values = {
                    "section_type": SectionType(section_dict["name"]),
                    "parent_item_id": item_dict["product_id"],
                    "child_item_id": section_item["product_id"],
                }
                # print(section_dict["name"], item_dict["product_id"], section_item["product_id"])
                with Session() as db:
                    try:
                        obj = Sections(**values)
                        db.add(obj)
                        db.commit()
                    except Exception as e:
                        pass
                        # print(e)


def insert_all_departments():
    departments = get_departments()
    for department in departments.values():
        print(department["name"])
        insert_department(department_dict=department)


def insert_all_aisles():
    aisles = get_aisles()
    for aisle in aisles.values():
        print(aisle["name"])
        insert_aisle(aisle_dict=aisle)


def insert_all_items():
    items = get_items()
    for item in items.values():
        print(item["name"])
        insert_item(item_dict=item)


def insert_all_sections():
    items = get_items()
    for item in items.values():
        # print(item["name"])
        insert_sections(item_dict=item)


def insert_item_by_index(index: int):
    items = get_items()
    keys = list(items.keys())
    item = items[keys[index]]
    insert_item(item_dict=item)


def insert_section_by_index(index: int):
    items = get_items()
    keys = list(items.keys())
    item = items[keys[index]]
    insert_sections(item_dict=item)
