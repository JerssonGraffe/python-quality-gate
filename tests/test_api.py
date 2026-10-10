from fastapi.testclient import TestClient

import main
from app import db


def test_task_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "tasks.db")
    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/tasks").json() == []
        assert client.post("/tasks", json={"title": "   "}).status_code == 422

        created = client.post(
            "/tasks", json={"title": " Comprar pan ", "description": "Integral"}
        )
        assert created.status_code == 201
        task = created.json()
        assert task["title"] == "Comprar pan"
        assert task["description"] == "Integral"
        assert task["completed"] is False
        assert task["project_id"] is None
        assert task["created_at"]
        task_id = task["id"]

        assert client.get(f"/tasks/{task_id}").json() == task
        assert client.get("/tasks?completed=false").json() == [task]
        assert client.get("/tasks?completed=true").json() == []

        updated = client.put(
            f"/tasks/{task_id}", json={"title": "Pan", "completed": True}
        )
        assert updated.status_code == 200
        assert updated.json()["completed"] is True
        assert updated.json()["description"] == ""
        assert client.get("/tasks?completed=true").json() == [updated.json()]

    # Los datos sobreviven a un reinicio de la aplicación.
    with TestClient(main.app) as client:
        assert client.get(f"/tasks/{task_id}").json() == updated.json()
        assert client.delete(f"/tasks/{task_id}").status_code == 204
        assert client.get(f"/tasks/{task_id}").status_code == 404
        assert (
            client.put(
                f"/tasks/{task_id}", json={"title": "Pan", "completed": False}
            ).status_code
            == 404
        )
        assert client.delete(f"/tasks/{task_id}").status_code == 404
        assert client.get("/tasks").json() == []
