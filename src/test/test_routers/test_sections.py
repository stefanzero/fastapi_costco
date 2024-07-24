from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from box import Box, BoxList
from src.models import Department, Product, Section, SectionType


def test_read_sections(client: TestClient, test_departments_with_sections: BoxList):
    expected_sections = BoxList([])
    for department in test_departments_with_sections:
        for aisle in department.aisles:
            for product in aisle.products:
                for section_type, product_list in sorted(product.sections.items()):
                    for child_product in product_list:
                        expected_sections.append(
                            Box(
                                {
                                    "section_type": SectionType[section_type].value,
                                    "parent_product_id": product.product_id,
                                    "child_product_id": child_product.product_id,
                                }
                            )
                        )
    response = client.get(f"/sections")
    assert response.status_code == status.HTTP_200_OK
    actual_sections = BoxList(response.json())
    assert len(actual_sections) == len(expected_sections)
    assert actual_sections == expected_sections


def test_read_section(client: TestClient, test_departments_with_sections: BoxList):
    expected_section = BoxList([])
    for department in test_departments_with_sections:
        for aisle in department.aisles:
            for product in aisle.products:
                for section_type, product_list in sorted(product.sections.items()):
                    child_product = product_list[0]
                    section_type = SectionType[section_type]
                    parent_product_id = product.product_id
                    child_product_id = child_product.product_id
                    expected_section = Box(
                        {
                            "section_type": section_type.value,
                            "parent_product_id": parent_product_id,
                            "child_product_id": child_product_id,
                        }
                    )
    response = client.get(
        f"/sections/{section_type.value}/{parent_product_id}/{child_product_id}"
    )
    assert response.status_code == status.HTTP_200_OK
    actual_section = Box(response.json())
    assert actual_section == expected_section


def test_read_section_not_found(client: TestClient):
    section_type = SectionType["featured_products"]
    fake_parent_product_id = 1
    fake_child_product_id = 1
    response = client.get(
        f"/sections/{section_type.value}/{fake_parent_product_id}/{fake_child_product_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_section(client: TestClient, test_departments: Box, db: Session):
    department = test_departments[0]
    aisle = department.aisles[0]
    products = aisle.products
    section_type = SectionType["featured_products"]
    parent_product_id = products[0].product_id
    child_product_id = products[1].product_id
    request_data = {
        "section_type": section_type,
        "parent_product_id": parent_product_id,
        "child_product_id": child_product_id,
    }
    response = client.post("/sections", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    actual_section = (
        #
        db.query(Section)
        .filter(Section.section_type == section_type)
        .filter(Section.parent_product_id == parent_product_id)
        .filter(Section.parent_product_id == parent_product_id)
        .first()
    )
    for key, value in request_data.items():
        assert getattr(actual_section, key) == value


def test_create_section_validation_error(
    client: TestClient, test_departments: Box, db: Session
):
    department = test_departments[0]
    aisle = department.aisles[0]
    products = aisle.products
    section_type = SectionType["featured_products"]
    parent_product_id = products[0].product_id
    child_product_id = parent_product_id
    request_data = {
        "section_type": section_type,
        "parent_product_id": parent_product_id,
        "child_product_id": child_product_id,
    }
    response = client.post("/sections", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_section_integrity_error(
    client: TestClient, test_departments: Box, db: Session
):
    department = test_departments[0]
    aisle = department.aisles[0]
    products = aisle.products
    section_type = SectionType["featured_products"]
    parent_product_id = products[0].product_id
    fake_child_product_id = 1
    request_data = {
        "section_type": section_type,
        "parent_product_id": parent_product_id,
        "child_product_id": fake_child_product_id,
    }
    response = client.post("/sections", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_section(
    test_departments_with_sections: BoxList[Department], client: TestClient, db: Session
):
    department = test_departments_with_sections[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    parent_product_id = product.product_id
    section_type = SectionType["featured_products"].value
    featured_products = product.sections.featured_products
    child_product_id = featured_products[0].product_id

    response = client.delete(
        f"/sections/{section_type}/{parent_product_id}/{child_product_id}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_section_not_found(
    test_departments_with_sections: BoxList[Department], client: TestClient, db: Session
):
    department = test_departments_with_sections[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    parent_product_id = product.product_id
    section_type = SectionType["featured_products"].value
    child_product_id = parent_product_id

    response = client.delete(
        f"/sections/{section_type}/{parent_product_id}/{child_product_id}",
        # json=request_data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
