from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from box import Box, BoxList
from src.models import Department, Aisle


def test_read_departments(client: TestClient, test_departments: BoxList[Department]):
    response = client.get(f"/departments/")
    assert response.status_code == status.HTTP_200_OK
    actual_departments = BoxList(response.json())
    expected_departments = BoxList()
    for department in test_departments:
        delattr(department, "aisles")
        expected_departments.append(department)
    assert len(actual_departments) == len(test_departments)
    assert actual_departments == expected_departments


def test_read_department_not_found(client: TestClient):
    response = client.get(f"/departments/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_department(client: TestClient, test_departments: BoxList[Department]):
    expected_department = test_departments[0]
    delattr(expected_department, "aisles")
    department_id = expected_department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles=false")
    assert response.status_code == status.HTTP_200_OK
    actual_department = Box(response.json())
    assert actual_department == expected_department


def test_read_department_with_aisles(
    client: TestClient, test_departments: BoxList[Department]
):
    expected_department = test_departments[0]
    for aisle in expected_department.aisles:
        delattr(aisle, "products")
    department_id = expected_department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles=true")
    assert response.status_code == status.HTTP_200_OK
    actual_department = Box(response.json())
    assert len(actual_department.aisles) == len(expected_department.aisles)
    assert actual_department == expected_department


def test_read_department_with_aisles_and_products(
    client: TestClient, test_departments: BoxList[Department]
):
    expected_department = test_departments[0]
    department_id = expected_department.department_id
    response = client.get(f"/departments/{department_id}?with_aisles_and_products=true")
    assert response.status_code == status.HTTP_200_OK
    actual_department = Box(response.json())
    assert actual_department == expected_department
    assert len(actual_department.aisles) == 2
    assert len(actual_department.aisles[0].products) == 2


def test_create_department(client: TestClient, db: Session):
    request_data = {"department_id": 1, "name": "Wines", "rank": 1}
    response = client.post("/departments", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    actual_department = db.query(Department).filter(Department.id == 1).first()
    for key, value in request_data.items():
        assert getattr(actual_department, key) == value


def test_create_department_conflict(
    client: TestClient, db: Session, test_departments: Box
):
    department_id = test_departments[0].department_id
    request_data = {"department_id": department_id, "name": "Wines", "rank": 1}
    response = client.post("/departments", json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_department(
    test_departments: BoxList[Department], client: TestClient, db: Session
):
    request_data = {"department_id": 1, "name": "Wines", "rank": 1}
    response = client.put(f"/departments/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    actual_department = db.query(Department).filter(Department.id == 1).first()
    for key, value in request_data.items():
        assert getattr(actual_department, key) == value


def test_update_department_not_found(client: TestClient, db: Session):
    request_data = {"department_id": 1, "name": "Wines", "rank": 1}
    response = client.put("/departments/1", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Department not found."}


def test_delete_department(
    client: TestClient, test_departments: BoxList[Department], db: Session
):
    department = test_departments[0]
    department_id = department.department_id
    response = client.delete(f"/departments/{department_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    model = (
        db.query(Department).filter(Department.department_id == department_id).first()
    )
    assert model is None
    # check cascade
    aisles = db.query(Aisle).filter(Aisle.department_id == department_id).all()
    assert len(aisles) == 0


def test_delete_department_not_found(client: TestClient, db: Session):
    department_id = 1
    response = client.delete(f"/departments/{department_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Department not found."}
