import sqlite3

from fastapi.testclient import TestClient

from app import db
from main import app


def test_projects_and_assigned_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "tasks.db")
    with TestClient(app) as client:
        assert client.get("/projects").json() == []
        assert client.post("/projects", json={"name": "  "}).status_code == 422
        response = client.post(
            "/projects", json={"name": " Casa ", "description": "Reformas"}
        )
        assert response.status_code == 201
        project = response.json()
        project_id = project["id"]
        assert project["name"] == "Casa"
        assert client.get(f"/projects/{project_id}").json() == project
        assert client.get("/projects").json() == [project]
        assert (
            client.post(
                "/tasks", json={"title": "Pintar", "project_id": 999}
            ).status_code
            == 404
        )

        task = client.post(
            "/tasks", json={"title": "Pintar", "project_id": project_id}
        ).json()
        assert task["project_id"] == project_id
        assert client.get(f"/tasks?project_id={project_id}&completed=false").json() == [
            task
        ]
        assert client.get("/tasks?project_id=999").json() == []
        assert (
            client.put(
                f"/tasks/{task['id']}",
                json={"title": "Pintar", "completed": True, "project_id": 999},
            ).status_code
            == 404
        )
        assert client.get(f"/tasks/{task['id']}").json() == task
        assert client.delete(f"/projects/{project_id}").status_code == 409

    with TestClient(app) as client:
        assert client.get(f"/tasks/{task['id']}").json() == task
        updated = client.put(f"/projects/{project_id}", json={"name": "Jardín"})
        assert updated.json()["name"] == "Jardín"
        assert (
            client.put(
                f"/tasks/{task['id']}", json={"title": "Pintar", "completed": True}
            ).json()["project_id"]
            is None
        )
        assert client.delete(f"/projects/{project_id}").status_code == 204
        assert client.get(f"/projects/{project_id}").status_code == 404
        assert (
            client.put(f"/projects/{project_id}", json={"name": "Otra"}).status_code
            == 404
        )
        assert client.delete(f"/projects/{project_id}").status_code == 404
        assert client.get(f"/tasks/{task['id']}").json()["completed"] is True


def test_existing_database_is_upgraded(tmp_path, monkeypatch):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as connection:
        connection.execute("""CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        connection.execute("INSERT INTO tasks (title) VALUES ('Tarea anterior')")

    monkeypatch.setattr(db, "DATABASE_PATH", path)
    with TestClient(app) as client:
        assert client.get("/tasks/1").json()["project_id"] is None
        project_id = client.post("/projects", json={"name": "Nuevo"}).json()["id"]
        assert (
            client.put(
                "/tasks/1",
                json={
                    "title": "Tarea anterior",
                    "completed": False,
                    "project_id": project_id,
                },
            ).json()["project_id"]
            == project_id
        )
        assert client.delete(f"/projects/{project_id}").status_code == 409

    with TestClient(app) as client:
        assert client.get("/tasks/1").json()["project_id"] == project_id
