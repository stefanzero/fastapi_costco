from fastapi import status
from box import Box

def test_read_department_not_found(client):
    response = client.get(f"/departments/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_department(client, test_departments: Box):
    department = test_departments[0]
    delattr(department, "aisles")
    department_id = department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles=false")
    assert response.status_code == status.HTTP_200_OK
    response_department = Box(response.json())
    assert response_department == department


def test_read_department_with_aisles(client, test_departments: Box):
    department = test_departments[0]
    for aisle in department.aisles:
        delattr(aisle, "products")
    department_id = department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles=true")
    assert response.status_code == status.HTTP_200_OK
    response_department = Box(response.json())
    assert response_department == department
    assert len(response_department.aisles) == 2


def test_read_department_with_aisles_and_products(client, test_departments: Box):
    department = test_departments[0]
    department_id = department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles_and_products=true")
    assert response.status_code == status.HTTP_200_OK
    response_department = Box(response.json())
    assert response_department == department
    assert len(response_department.aisles) == 2
    assert len(response_department.aisles[0].products) == 2
