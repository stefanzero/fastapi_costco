from fastapi import status
from box import Box, BoxList


def test_read_product(client, test_departments: BoxList):
    department = test_departments[0]
    aisle = department.aisles[0]
    product = aisle.products[0]
    product.aisle_id = aisle.aisle_id
    product_id = product.product_id
    response = client.get(f"/products/{product_id}")
    assert response.status_code == status.HTTP_200_OK
    response_product = Box(response.json())
    assert response_product == product
