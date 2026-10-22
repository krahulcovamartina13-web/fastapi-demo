"""End-to-end integrační test proti reálně běžícímu uvicorn serveru přes skutečné HTTP."""
import httpx


def test_full_task_lifecycle_over_http(live_server):
    with httpx.Client(base_url=live_server, timeout=5) as http:
        # Create
        r = http.post("/tasks", json={"title": "E2E úkol"})
        assert r.status_code == 201
        tid = r.json()["id"]

        # Read
        assert http.get(f"/tasks/{tid}").json()["title"] == "E2E úkol"

        # Update
        r = http.patch(f"/tasks/{tid}", json={"done": True})
        assert r.json()["done"] is True

        # List
        assert any(t["id"] == tid for t in http.get("/tasks").json())

        # Delete
        assert http.delete(f"/tasks/{tid}").status_code == 204
        assert http.get(f"/tasks/{tid}").status_code == 404
