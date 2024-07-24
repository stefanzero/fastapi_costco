from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from box import Box, BoxList
from src.models import Aisle, Department, Product


def test_read_aisles(client: TestClient, test_departments: BoxList[Department]):
    response = client.get(f"/aisles/")
    assert response.status_code == status.HTTP_200_OK
    actual_aisles = BoxList(response.json())
    expected_aisles = BoxList()
    for department in test_departments:
        for aisle in department.aisles:
            delattr(aisle, "products")
            expected_aisles.append(aisle)
    assert len(actual_aisles) == len(expected_aisles)
    assert actual_aisles == expected_aisles


def test_read_aisle(client: TestClient, test_departments: BoxList[Department]):
    expected_department = test_departments[0]
    expected_aisle = expected_department.aisles[0]
    delattr(expected_aisle, "products")
    aisle_id = expected_aisle.aisle_id
    response = client.get(f"/aisles/{aisle_id}")
    assert response.status_code == status.HTTP_200_OK
    actual_aisle = Box(response.json())
    assert actual_aisle == expected_aisle


def test_read_aisle_with_products(
    client: TestClient, test_departments: BoxList[Department]
):
    expected_department = test_departments[0]
    expected_aisle = expected_department.aisles[0]
    aisle_id = expected_aisle.aisle_id
    response = client.get(f"/aisles/{aisle_id}?with_products=true")
    assert response.status_code == status.HTTP_200_OK
    actual_aisle = Box(response.json())
    assert actual_aisle == expected_aisle


def test_read_aisle_not_found(client: TestClient, test_departments_data):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    response = client.get(f"/aisles/{aisle_ids[0]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_aisles_by_department(
    client: TestClient, test_departments: BoxList[Department]
):
    expected_department = test_departments[0]
    department_id = expected_department.department_id
    expected_aisles = BoxList()
    for aisle in expected_department.aisles:
        delattr(aisle, "products")
        expected_aisles.append(aisle)
    response = client.get(f"/aisles/by_department/{department_id}")
    assert response.status_code == status.HTTP_200_OK
    actual_aisles = BoxList(response.json())
    assert actual_aisles == expected_aisles


def test_create_aisle(client: TestClient, test_departments: Box, db: Session):
    department = test_departments[0]
    aisle = department.aisles[0]
    new_aisle_id = 103
    request_data = {
        "aisle_id": new_aisle_id,
        "department_id": aisle.department_id,
        "name": "Sparkling Wines",
        "rank": 3,
    }
    response = client.post("/aisles", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    actual_aisle = db.query(Aisle).filter(Aisle.aisle_id == new_aisle_id).first()
    for key, value in request_data.items():
        assert getattr(actual_aisle, key) == value


def test_create_aisle_conflict(client: TestClient, test_departments: Box):
    department = test_departments[0]
    aisle = department.aisles[0]
    request_data = {
        "aisle_id": aisle.aisle_id,
        "department_id": aisle.department_id,
        "name": "Sparkling Wines",
        "rank": 3,
    }
    response = client.post("/aisles", json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_aisle_integrity_error(client: TestClient, test_departments: Box):
    department = test_departments[0]
    aisle = department.aisles[0]
    fake_department_id = 3
    new_aisle_id = 103
    request_data = {
        "aisle_id": new_aisle_id,
        "department_id": fake_department_id,
        "name": "Sparkling Wines",
        "rank": 3,
    }
    response = client.post("/aisles", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_aisle(
    test_departments: BoxList[Department], client: TestClient, db: Session
):
    department = test_departments[0]
    aisle = department.aisles[0]
    new_rank = 3
    request_data = {
        "aisle_id": aisle.aisle_id,
        "department_id": aisle.department_id,
        "name": aisle.name,
        "rank": new_rank,
    }
    response = client.put(f"/aisles/{aisle.aisle_id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    actual_aisle = db.query(Aisle).filter(Aisle.aisle_id == aisle.aisle_id).first()
    for key, value in request_data.items():
        assert getattr(actual_aisle, key) == value


def test_update_aisle_not_found(
    test_departments: BoxList[Department], client: TestClient, db: Session
):
    department = test_departments[0]
    aisle = department.aisles[0]
    fake_aisle_id = 103
    request_data = {
        "aisle_id": fake_aisle_id,
        "department_id": aisle.department_id,
        "name": aisle.name,
        "rank": aisle.rank,
    }
    response = client.put(f"/aisles/{fake_aisle_id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_aisle_integrity_error(
    test_departments: BoxList[Department], client: TestClient, db: Session
):
    department = test_departments[0]
    aisle = department.aisles[0]
    fake_department_id = 3
    request_data = {
        "aisle_id": aisle.aisle_id,
        "department_id": fake_department_id,
        "name": aisle.name,
        "rank": aisle.rank,
    }
    response = client.put(f"/aisles/{aisle.aisle_id}", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_aisle(
    client: TestClient, test_departments: BoxList[Department], db: Session
):
    department = test_departments[0]
    aisle = department.aisles[0]
    aisle_id = aisle.aisle_id
    response = client.delete(f"/aisles/{aisle_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    model = db.query(Aisle).filter(Aisle.aisle_id == aisle_id).first()
    assert model is None
    # check cascade
    products = db.query(Product).filter(Product.aisle_id == aisle_id).all()
    assert len(products) == 0


def test_delete_aisle_not_found(
    client: TestClient, test_departments: BoxList[Department], db: Session
):
    department = test_departments[0]
    last_aisle = department.aisles[-1]
    fake_aisle_id = last_aisle.aisle_id + 1
    response = client.delete(f"/aisles/{fake_aisle_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
