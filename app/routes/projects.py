import sqlite3

from fastapi import APIRouter, HTTPException, Response, status

from app.db import database
from app.schemas import Project, ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])


def project_or_404(connection: sqlite3.Connection, project_id: int) -> dict:
    row = connection.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return dict(row)


@router.get("", response_model=list[Project])
def list_projects():
    with database() as connection:
        rows = connection.execute("SELECT * FROM projects ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    with database() as connection:
        cursor = connection.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (project.name, project.description),
        )
        return project_or_404(connection, cursor.lastrowid)


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: int):
    with database() as connection:
        return project_or_404(connection, project_id)


@router.put("/{project_id}", response_model=Project)
def update_project(project_id: int, project: ProjectCreate):
    with database() as connection:
        cursor = connection.execute(
            "UPDATE projects SET name = ?, description = ? WHERE id = ?",
            (project.name, project.description, project_id),
        )
        if not cursor.rowcount:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project_or_404(connection, project_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int):
    with database() as connection:
        try:
            cursor = connection.execute(
                "DELETE FROM projects WHERE id = ?", (project_id,)
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=409, detail="El proyecto contiene tareas"
            ) from error
        if not cursor.rowcount:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
