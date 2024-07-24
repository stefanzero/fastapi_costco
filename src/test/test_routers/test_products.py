import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from box import Box, BoxList
from src.models import Department, Product


def test_read_products(client: TestClient, test_departments: BoxList):
    expected_products = BoxList([])
    for department in test_departments:
        for aisle in department.aisles:
            for product in aisle.products:
                expected_products.append(product)
    response = client.get(f"/products")
    assert response.status_code == status.HTTP_200_OK
    actual_products = BoxList(response.json())
    assert len(actual_products) == len(expected_products)


def test_read_product(client: TestClient, test_departments: BoxList):
    expected_department = test_departments[0]
    expected_aisle = expected_department.aisles[0]
    expected_product = expected_aisle.products[0]
    expected_product.aisle_id = expected_aisle.aisle_id
    product_id = expected_product.product_id
    response = client.get(f"/products/{product_id}")
    assert response.status_code == status.HTTP_200_OK
    actual_product = Box(response.json())
    assert actual_product == expected_product


def test_read_product_not_found(client: TestClient, test_departments_data):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    aisle = department.aisles[aisle_ids[0]]
    product_ids = list(aisle.products.keys())
    response = client.get(f"/products/{product_ids[0]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# @pytest.mark.skip(reason="Fix infinite recursion on section.child")
def test_read_product_with_sections(
    client: TestClient, test_departments_with_sections: BoxList
):
    expected_department = test_departments_with_sections[0]
    expected_aisle = expected_department.aisles[0]
    expected_product = expected_aisle.products[0]
    expected_product.aisle_id = expected_aisle.aisle_id
    product_id = expected_product.product_id
    response = client.get(f"/products/{product_id}?with_sections=true")
    assert response.status_code == status.HTTP_200_OK
    actual_product = Box(response.json())
    assert actual_product == expected_product


def test_read_products_by_aisle(
    client: TestClient, test_departments: BoxList[Department]
):
    expected_department = test_departments[0]
    expected_aisle = expected_department.aisles[0]
    expected_products = BoxList([])
    for product in expected_aisle.products:
        expected_products.append(product)
    response = client.get(f"/products/by_aisle/{expected_aisle.aisle_id}")
    assert response.status_code == status.HTTP_200_OK
    actual_products = BoxList(response.json())
    assert len(actual_products) == len(expected_products)


def test_read_products_by_aisle_not_found(client: TestClient, test_departments_data):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    response = client.get(f"/products/by_aisle/{aisle_ids[0]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_products_by_department(
    client: TestClient, test_departments: BoxList[Department]
):
    expected_department = test_departments[0]
    expected_products = BoxList([])
    for aisle in expected_department.aisles:
        for product in aisle.products:
            expected_products.append(product)
    response = client.get(
        f"/products/by_department/{expected_department.department_id}"
    )
    assert response.status_code == status.HTTP_200_OK
    actual_products = BoxList(response.json())
    assert len(actual_products) == len(expected_products)


def test_read_products_by_department_not_found(
    client: TestClient, test_departments_data
):
    department_ids = list(test_departments_data.keys())
    response = client.get(f"/products/by_department/{department_ids[0]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_product(
    client: TestClient, db: Session, test_departments: BoxList[Department]
):
    department = test_departments[0]
    aisle = department.aisles[0]
    request_data = {
        "product_id": 1003,
        "aisle_id": aisle.aisle_id,
        "name": "test product",
        "rank": 3,
        "src": "",
        "size": "",
        "alt": "",
        "price": "",
        "price_per": "",
        "affix": "",
    }
    response = client.post("/products", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = request_data["product_id"]
    actual_product = db.query(Product).filter(Product.product_id == product_id).first()
    for key, value in request_data.items():
        assert getattr(actual_product, key) == value


def test_create_product_conflict_error(
    client: TestClient, db: Session, test_departments: BoxList[Department]
):
    department = test_departments[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    request_data = {
        "product_id": product.product_id,
        "aisle_id": aisle.aisle_id,
        "name": "test product",
        "rank": 3,
        "src": "",
        "size": "",
        "alt": "",
        "price": "",
        "price_per": "",
        "affix": "",
    }
    response = client.post("/products", json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_product_integrity_error(
    client: TestClient, test_departments_data: BoxList[Department]
):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    aisle = department.aisles[aisle_ids[0]]
    request_data = {
        "product_id": 1003,
        "aisle_id": aisle.aisle_id,
        "name": "test product",
        "rank": 3,
        "src": "",
        "alt": "",
        "price": "",
        "price_per": "",
        "affix": "",
    }
    response = client.post("/products", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_product(client: TestClient, test_departments: BoxList[Department]):
    department = test_departments[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    request_data = {
        "product_id": product.product_id,
        "aisle_id": aisle.aisle_id,
        "name": "test product",
        "rank": 3,
        "src": product.src,
        "size": product.size,
        "alt": product.alt,
        "price": product.price,
        "price_per": product.price_per,
        "affix": product.affix,
    }
    response = client.put(f"/products/{product.product_id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_product_not_found(
    client: TestClient, test_departments_data: BoxList[Department]
):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    aisle = department.aisles[aisle_ids[0]]
    product_ids = list(aisle.products.keys())
    product = aisle.products[product_ids[0]]
    request_data = {
        "product_id": product.product_id,
        "aisle_id": aisle.aisle_id,
        "name": "test product",
        "rank": 3,
        "src": product.src,
        "size": product.size,
        "alt": product.alt,
        "price": product.price,
        "price_per": product.price_per,
        "affix": product.affix,
    }
    response = client.put(f"/products/{product.product_id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_product_integrity_error(
    client: TestClient, test_departments: BoxList[Department]
):
    department = test_departments[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    fake_aisle_id = 1
    request_data = {
        "product_id": product.product_id,
        "aisle_id": fake_aisle_id,
        "name": "test product",
        "rank": 3,
        "src": product.src,
        "size": product.size,
        "alt": product.alt,
        "price": product.price,
        "price_per": product.price_per,
        "affix": product.affix,
    }
    response = client.put(f"/products/{product.product_id}", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_patch_product(client: TestClient, test_departments: BoxList[Department]):
    department = test_departments[0]
    aisle = department.aisles[0]
    next_aisle = department.aisles[1]
    product = aisle.products[0]
    request_data = {
        "product_id": product.product_id,
        "aisle_id": next_aisle.aisle_id,
    }
    response = client.patch(f"/products/{product.product_id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_patch_product_not_found(
    client: TestClient, test_departments_data: BoxList[Department]
):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    aisle = department.aisles[aisle_ids[0]]
    product_ids = list(aisle.products.keys())
    product = aisle.products[product_ids[0]]
    request_data = {
        "product_id": product.product_id,
        "name": "test product",
    }
    response = client.patch(f"/products/{product.product_id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_patch_product_integrity_error(
    client: TestClient, test_departments: BoxList[Department]
):
    department = test_departments[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    fake_aisle_id = 1
    request_data = {
        "product_id": product.product_id,
        "aisle_id": fake_aisle_id,
    }
    response = client.patch(f"/products/{product.product_id}", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_product(client: TestClient, test_departments: BoxList[Department]):
    department = test_departments[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    response = client.delete(f"/products/{product.product_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_product_not_found(
    client: TestClient, test_departments_data: BoxList[Department]
):
    department_ids = list(test_departments_data.keys())
    department = test_departments_data[department_ids[0]]
    aisle_ids = list(department.aisles.keys())
    aisle = department.aisles[aisle_ids[0]]
    product_ids = list(aisle.products.keys())
    product = aisle.products[product_ids[0]]
    response = client.delete(f"/products/{product.product_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
