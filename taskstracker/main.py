from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel, create_engine, Session, Field, select

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def get_session() :
    with Session(engine) as session:
        yield session

SessionDependency = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

app = FastAPI(lifespan=lifespan)

@app.post("/tasks/")
def create_task(task: Task, session: SessionDependency):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/")
def read_tasks(session: SessionDependency, offset: int = 0, limit: Annotated[int, Query(ge=1, le=100)] = 10):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

@app.get("/tasks/{task_id}")
def read_task(task_id: int, session: SessionDependency):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, session: SessionDependency):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDependency):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    session.delete(task)
    session.commit()
    return {"deleted": True}