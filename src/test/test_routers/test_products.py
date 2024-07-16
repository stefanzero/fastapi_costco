from fastapi import status
from box import Box, BoxList


def test_read_product(client, test_departments: BoxList):
    expected_department = test_departments[0]
    expected_aisle = expected_department.aisles[0]
    expected_product = expected_aisle.products[0]
    expected_product.aisle_id = expected_aisle.aisle_id
    product_id = expected_product.product_id
    response = client.get(f"/products/{product_id}")
    assert response.status_code == status.HTTP_200_OK
    actual_product = Box(response.json())
    assert actual_product == expected_product
