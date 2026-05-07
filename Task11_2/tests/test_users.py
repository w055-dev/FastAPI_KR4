import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from itertools import count
import main

fake = Faker()

@pytest.fixture(autouse=True)
def clean_db():
    main.db.clear()
    main._id_seq = count(start=1)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=main.app), 
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_user(client):
    user = {"username": fake.user_name(), "age": fake.random_int(1, 120)}
    r = await client.post("/users", json=user)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == 1
    assert data["username"] == user["username"]
    assert data["age"] == user["age"]


@pytest.mark.asyncio
async def test_get_user(client):
    user = {"username": fake.user_name(), "age": 25}
    created = await client.post("/users", json=user)
    user_id = created.json()["id"]
    r = await client.get(f"/users/{user_id}")
    assert r.status_code == 200
    assert r.json()["username"] == user["username"]


@pytest.mark.asyncio
async def test_get_user_404(client):
    r = await client.get("/users/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user(client):
    user = {"username": fake.user_name(), "age": 30}
    created = await client.post("/users", json=user)
    user_id = created.json()["id"]
    r = await client.delete(f"/users/{user_id}")
    assert r.status_code == 204
    assert (await client.get(f"/users/{user_id}")).status_code == 404


@pytest.mark.asyncio
async def test_delete_twice(client):
    user = {"username": fake.user_name(), "age": 30}
    created = await client.post("/users", json=user)
    user_id = created.json()["id"]
    await client.delete(f"/users/{user_id}")
    r = await client.delete(f"/users/{user_id}")
    assert r.status_code == 404