"""Integrační testy API přes FastAPI TestClient (pytest + httpx)."""
import pytest


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get_task(client):
    r = client.post("/tasks", json={"title": "Napsat testy", "description": "pytest"})
    assert r.status_code == 201
    task = r.json()
    assert task == {"id": 1, "title": "Napsat testy", "description": "pytest", "done": False}

    r = client.get(f"/tasks/{task['id']}")
    assert r.status_code == 200
    assert r.json() == task


def test_list_and_filter(client):
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B", "done": True})

    assert len(client.get("/tasks").json()) == 2
    done = client.get("/tasks", params={"done": True}).json()
    assert [t["title"] for t in done] == ["B"]


def test_partial_update(client):
    tid = client.post("/tasks", json={"title": "A", "description": "x"}).json()["id"]
    r = client.patch(f"/tasks/{tid}", json={"done": True})
    assert r.status_code == 200
    assert r.json() == {"id": tid, "title": "A", "description": "x", "done": True}


def test_delete(client):
    tid = client.post("/tasks", json={"title": "Smazat"}).json()["id"]
    assert client.delete(f"/tasks/{tid}").status_code == 204
    assert client.get(f"/tasks/{tid}").status_code == 404


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_not_found(client, method):
    kwargs = {"json": {"done": True}} if method == "patch" else {}
    r = getattr(client, method)("/tasks/999", **kwargs)
    assert r.status_code == 404
    assert r.json()["detail"] == "Task 999 not found"


@pytest.mark.parametrize(
    "payload",
    [
        {},                       # chybí title
        {"title": ""},            # prázdný title
        {"title": "x" * 101},     # příliš dlouhý
        {"title": "A", "done": "neni-bool"},
    ],
)
def test_validation_errors(client, payload):
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


def test_openapi_schema_available(client):
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Todo API"
    assert "/tasks/{task_id}" in schema["paths"]
