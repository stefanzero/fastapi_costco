import json
import os
from database import Session
from models import Departments

root_path = os.path.dirname(__file__)

data_cache = {}


def get_departments():
    if "departments" in data_cache:
        return data_cache["departments"]
    file_name = os.path.join(root_path, "departments.json")
    # print(file_name)
    with open(file_name) as file:
        file_contents = file.read()
        # print(file_contents)
        departments = json.loads(file_contents)
    data_cache["departments"] = departments
    return data_cache["departments"]


def insert_department(department_dict: dict):
    values = {
        "department_id": department_dict["id"],
        "name": department_dict["name"],
    }
    with Session() as db:
        try:
            obj = Departments(**values)
            db.add(obj)
            db.commit()
        except Exception as e:
            print(e)


def insert_by_index(index: int):
    departments = get_departments()
    keys = list(departments.keys())
    if index in range(len(keys)):
        department_dict = departments[keys[index]]
        print(department_dict["name"])
        insert_department(department_dict)


def insert_all_departments():
    departments = get_departments()
    for department in departments.values():
        print(department["name"])
        insert_department(department_dict=department)
