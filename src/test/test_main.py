# from sys import modules
from fastapi.testclient import TestClient
from src.main import app
from fastapi import status

client = TestClient(app)

# if "pytest" in modules:
#     print("pytest in modules")
# else:
#     print("pytest not in modules")


def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}
