from fastapi import status
from box import Box, BoxList
import json


def test_read_departments(client, test_departments: Box):
    response = client.get(f"/departments/")
    assert response.status_code == status.HTTP_200_OK
    departments = BoxList(response.json())
    assert len(departments) == 2


def test_read_department_not_found(client):
    response = client.get(f"/departments/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_department(client, test_departments: Box):
    expected_department = test_departments[0]
    delattr(expected_department, "aisles")
    department_id = expected_department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles=false")
    assert response.status_code == status.HTTP_200_OK
    actual_department = Box(response.json())
    assert actual_department == expected_department


def test_read_department_with_aisles(client, test_departments: Box):
    expected_department = test_departments[0]
    for aisle in expected_department.aisles:
        delattr(aisle, "products")
    department_id = expected_department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles=true")
    assert response.status_code == status.HTTP_200_OK
    actual_department = Box(response.json())
    assert actual_department == expected_department
    assert len(actual_department.aisles) == 2


def test_read_department_with_aisles_and_products(client, test_departments: Box):
    expected_department = test_departments[0]
    department_id = expected_department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles_and_products=true")
    assert response.status_code == status.HTTP_200_OK
    actual_department = Box(response.json())
    assert actual_department == expected_department
    assert len(actual_department.aisles) == 2
    assert len(actual_department.aisles[0].products) == 2
