from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]


class ProjectCreate(BaseModel):
    name: Name
    description: str = Field(default="", max_length=1000)


class Project(ProjectCreate):
    id: int
    created_at: str


class TaskCreate(BaseModel):
    title: Name
    description: str = Field(default="", max_length=1000)
    project_id: int | None = Field(default=None, gt=0)


class TaskUpdate(TaskCreate):
    completed: bool


class Task(TaskUpdate):
    id: int
    created_at: str
