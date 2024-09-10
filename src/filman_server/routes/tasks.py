# for what purpose rabbitmq exists
# if you can build your task broker and learn something :~~~~D

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post(
    "/create",
    response_model=schemas.Task,
    summary="Create a task",
    description="Create a task to do",
)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    task.task_created = datetime.now()
    task.task_started = None
    task.task_finished = None

    db_task = crud.create_task(db, task)
    return db_task


@tasks_router.head(
    "/get/task/to_do",
    summary="Check if is any task to do",
    description="Check if is any task to do for given task types (only check)",
)
def get_task_to_do_head(task_types: List[schemas.TaskTypes] = Query(...), db: Session = Depends(get_db)):
    db_task = crud.get_task_to_do(db, task_types, head=True)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={"task_id": db_task.task_id})


@tasks_router.get(
    "/get/task/to_do",
    response_model=schemas.Task,
    summary="Get task to do",
    description="Get task to do for given task types",
)
def get_task_to_do(task_types: List[schemas.TaskTypes] = Query(...), db: Session = Depends(get_db)):
    db_task = crud.get_task_to_do(db, task_types, head=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@tasks_router.get(
    "/update/task/status/{task_id}/{task_status}",
    response_model=schemas.Task,
    summary="Update task status",
    description="Update task status to given status",
)
def update_task_status(task_id: int, task_status: schemas.TaskStatus, db: Session = Depends(get_db)):
    db_task = crud.update_task_status(db, task_id, task_status)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
