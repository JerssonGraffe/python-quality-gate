from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db
from app.routes import projects, tasks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.initialize()
    yield


app = FastAPI(title="API de proyectos y tareas", lifespan=lifespan)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
