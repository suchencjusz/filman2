from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from filman_server.database import crud, models, schemas
from filman_server.database.db import SessionLocal, engine, get_db

from typing import Optional, List, Dict, Any

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post("/create", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    task.task_created = datetime.now()
    task.task_started = None
    task.task_finished = None

    db_task = crud.create_task(db, task)
    return db_task


@tasks_router.head("/get/task/to_do")
def get_task_to_do_head(task_types: List[schemas.TaskTypes] = Query(...), db: Session = Depends(get_db)):
    db_task = crud.get_task_to_do(db, task_types, head=True)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={"task_id": db_task.task_id})


@tasks_router.get("/get/task/to_do", response_model=schemas.Task)
def get_task_to_do(task_types: List[schemas.TaskTypes] = Query(...), db: Session = Depends(get_db)):
    db_task = crud.get_task_to_do(db, task_types, head=False)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


#
#
#


@tasks_router.get("/update/task/status/{task_id}/{task_status}", response_model=schemas.Task)
def update_task_status(task_id: int, task_status: schemas.TaskStatus, db: Session = Depends(get_db)):
    db_task = crud.update_task_status(db, task_id, task_status)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
