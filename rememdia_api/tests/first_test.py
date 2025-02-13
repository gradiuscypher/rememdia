from fastapi.testclient import TestClient
from api import app  # Import your FastAPI app

client = TestClient(app)


# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello World"}


# def test_create_item():
#     response = client.post(
#         "/items/",
#         json={"name": "Test Item", "price": 10.5},
#     )
#     assert response.status_code == 200
#     assert response.json() == {
#         "name": "Test Item",
#         "price": 10.5,
#         "id": 1,
#     }
def test_example():
    assert True == True
