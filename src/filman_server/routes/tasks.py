# for what purpose rabbitmq exists
# if you can build your task broker and learn something :~~~~D (not doing it)

import logging
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

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
    "/get/to_do",
    summary="Check if is any task to do",
    description="Check if is any task to do for given task types (only check)",
)
def get_task_to_do_head(
    task_types: List[schemas.TaskTypes] = Query(...),
    db: Session = Depends(get_db),
):
    db_task = crud.get_task_to_do(db, task_types, head=True)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={"task_id": db_task.task_id})


@tasks_router.get(
    "/get/to_do",
    response_model=schemas.Task,
    summary="Get task to do",
    description="Get task to do for given task types",
)
def get_task_to_do(
    task_types: List[schemas.TaskTypes] = Query(...),
    db: Session = Depends(get_db),
):
    db_task = crud.get_task_to_do(db, task_types, head=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@tasks_router.get(
    "/update/status/{task_id}/{task_status}",
    response_model=schemas.Task,
    summary="Update task status",
    description="Update task status to given status",
)
def update_task_status(task_id: int, task_status: schemas.TaskStatus, db: Session = Depends(get_db)):
    db_task = crud.update_task_status(db, task_id, task_status)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@tasks_router.get(
    "/update/stuck/{minutes}",
    response_model=bool,
    summary="Update stuck tasks",
    description="Update stuck tasks to 'queued' status from 'running'",
)
def update_stuck_tasks(minutes: int, db: Session = Depends(get_db)):
    db_tasks = crud.update_stuck_tasks(db, minutes)

    if db_tasks is None:
        raise HTTPException(status_code=400, detail="Tasks not updated! Something went wrong")
    return True


@tasks_router.get(
    "/update/old/{minutes}",
    response_model=bool,
    summary="Update old tasks",
    description="Update old tasks, remove tasks older than X minutes",
)
def update_old_tasks(minutes: int, db: Session = Depends(get_db)):
    db_tasks = crud.update_old_tasks(db, minutes)

    if db_tasks is None:
        raise HTTPException(status_code=400, detail="Tasks not updated! Something went wrong")
    return True


#
# MULTIPLE TASKS CREATION
#


@tasks_router.get(
    "/new/scrap/filmweb/users/movies",
    response_model=bool,
    summary="Add scrap users task",
    description="Add task to scrap users movies (watched movies)",
)
def create_scrap_users_movies_task(db: Session = Depends(get_db)):
    db_task = crud.create_scrap_filmweb_users_movies_task(db)

    if db_task is None:
        raise HTTPException(status_code=400, detail="Tasks not created! Something went wrong")
    return True


@tasks_router.get(
    "/new/scrap/filmweb/movies",
    response_model=bool,
    summary="Add scrap movies task",
    description="Add task to scrap movies",
)
def create_scrap_movies_task(db: Session = Depends(get_db)):
    db_task = crud.create_scrap_filmweb_movies_task(db)

    if db_task is None:
        raise HTTPException(status_code=400, detail="Tasks not created! Something went wrong")
    return True


@tasks_router.get(
    "/new/scrap/filmweb/series",
    response_model=bool,
    summary="Add scrap series task",
    description="Add task to scrap series",
)
def create_scrap_series_task(db: Session = Depends(get_db)):
    db_task = crud.create_scrap_filmweb_series_task(db)

    if db_task is None:
        raise HTTPException(status_code=400, detail="Tasks not created! Something went wrong")
    return True


@tasks_router.get(
    "/new/scrap/filmweb/users/series",
    response_model=bool,
    summary="Add scrap users series task",
    description="Add task to scrap users series (watched series)",
)
def create_scrap_users_series_task(db: Session = Depends(get_db)):
    db_task = crud.create_scrap_filmweb_users_series_task(db)

    if db_task is None:
        raise HTTPException(status_code=400, detail="Tasks not created! Something went wrong")
    return True
