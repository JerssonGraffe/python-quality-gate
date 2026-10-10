import sqlite3

from fastapi import APIRouter, HTTPException, Response, status

from app.db import database
from app.schemas import Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def task_or_404(connection: sqlite3.Connection, task_id: int) -> dict:
    row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return dict(row)


@router.get("", response_model=list[Task])
def list_tasks(completed: bool | None = None, project_id: int | None = None):
    filters = []
    values = []
    if completed is not None:
        filters.append("completed = ?")
        values.append(completed)
    if project_id is not None:
        filters.append("project_id = ?")
        values.append(project_id)
    query = "SELECT * FROM tasks"
    if filters:
        query += " WHERE " + " AND ".join(filters)
    with database() as connection:
        rows = connection.execute(query + " ORDER BY id", values).fetchall()
    return [dict(row) for row in rows]


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    with database() as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO tasks (title, description, project_id) VALUES (?, ?, ?)",
                (task.title, task.description, task.project_id),
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=404, detail="Proyecto no encontrado"
            ) from error
        return task_or_404(connection, cursor.lastrowid)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    with database() as connection:
        return task_or_404(connection, task_id)


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate):
    with database() as connection:
        try:
            cursor = connection.execute(
                "UPDATE tasks SET title = ?, description = ?, completed = ?, "
                "project_id = ? WHERE id = ?",
                (
                    task.title,
                    task.description,
                    task.completed,
                    task.project_id,
                    task_id,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=404, detail="Proyecto no encontrado"
            ) from error
        if not cursor.rowcount:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return task_or_404(connection, task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with database() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if not cursor.rowcount:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
