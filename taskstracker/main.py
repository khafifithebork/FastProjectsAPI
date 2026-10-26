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