from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_example():
    assert True == True
