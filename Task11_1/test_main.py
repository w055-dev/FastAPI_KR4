from fastapi.testclient import TestClient
import pytest
from itertools import count
import main

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def reset_db():
    main.db.clear()
    main._id_seq = count(start=1)

class TestAPI:
    def test_create_user(self):
        response = client.post("/users", json={
            "username": "john", "age": 25
        })
        assert response.status_code == 201
        assert response.json()["username"] == "john"
        assert response.json()["id"] == 1
    
    def test_get_user(self):
        create_response = client.post("/users", json={"username": "john", "age": 25})
        assert create_response.status_code == 201
        response = client.get("/users/1")
        assert response.status_code == 200
        assert response.json()["username"] == "john"
    
    def test_get_user_404(self):
        response = client.get("/users/999")
        assert response.status_code == 404
    
    def test_delete_user(self):
        create_response = client.post("/users", json={"username": "temp", "age": 25})
        assert create_response.status_code == 201
        response = client.delete("/users/1")
        assert response.status_code == 204
        assert client.get("/users/1").status_code == 404
    
    def test_delete_user_404(self):
        response = client.delete("/users/999")
        assert response.status_code == 404