import os
import time

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql+psycopg2://taskuser:taskpass@task-db:5432/taskdb'
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)


class TaskCreate(BaseModel):
    title: str
    description: str
    is_completed: bool = False


class TaskResponse(TaskCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)
    yield
    engine.dispose()


app = FastAPI(title='Task Management API', lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/tasks', response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get('/tasks', response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id).all()


@app.get('/tasks/{task_id}', response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    return task


@app.delete('/tasks/{task_id}')
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    db.delete(task)
    db.commit()
    return {'message': 'Task deleted successfully'}
