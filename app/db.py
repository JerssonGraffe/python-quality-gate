import os
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

DATABASE_PATH = Path(os.getenv("TASKS_DB_PATH", "tasks.db"))


@contextmanager
def database():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            yield connection


def initialize():
    with database() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            project_id INTEGER REFERENCES projects(id) ON DELETE RESTRICT
        )""")
        # Las bases creadas por la primera versión ya tienen una tabla tasks.
        columns = connection.execute("PRAGMA table_info(tasks)").fetchall()
        if not any(column["name"] == "project_id" for column in columns):
            connection.execute(
                "ALTER TABLE tasks ADD COLUMN project_id INTEGER "
                "REFERENCES projects(id) ON DELETE RESTRICT"
            )
