import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db
from filman_server.tasks import scrap_movie

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post(
    "/create",
    summary="Create a task",
    description="Create a task and send it to Celery queue",
)
def create_task(task: schemas.TaskCreate):
    """
    Create a task and send it to Celery queue for processing.

    Args:
        task: Task creation data containing task_type and task_job

    Returns:
        dict: Task information including Celery task ID
    """
    try:
        # Send task to Celery queue
        celery_task = scrap_movie.delay(task.task_type, task.task_job)

        logging.info(f"Task sent to Celery queue: {celery_task.id}, type={task.task_type}, job={task.task_job}")

        return {
            "celery_task_id": celery_task.id,
            "task_type": task.task_type,
            "task_job": task.task_job,
            "status": "queued",
            "message": "Task sent to Celery queue successfully",
        }
    except Exception as e:
        logging.error(f"Failed to send task to Celery queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


#
# MULTIPLE TASKS CREATION
#


@tasks_router.get(
    "/new/scrap/filmweb/users/movies",
    response_model=dict,
    summary="Add scrap users task",
    description="Add tasks to scrap users movies (watched movies)",
)
def create_scrap_users_movies_task(db: Session = Depends(get_db)):
    """
    Create tasks for scraping all users' watched movies.
    Sends a Celery task for each user with filmweb mapping.
    """
    try:
        from filman_server.database import models

        filmweb_users = db.query(models.FilmWebUserMapping).all()
        task_ids = []

        for user in filmweb_users:
            celery_task = scrap_movie.delay(
                schemas.TaskTypes.SCRAP_FILMWEB_USER_WATCHED_MOVIES.value, str(user.filmweb_id)
            )
            task_ids.append(celery_task.id)

        logging.info(f"Sent {len(task_ids)} user movie scraping tasks to Celery queue")
        return {"status": "success", "tasks_queued": len(task_ids), "celery_task_ids": task_ids}
    except Exception as e:
        logging.error(f"Failed to create user movie scraping tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue tasks: {str(e)}")


@tasks_router.get(
    "/new/scrap/filmweb/movies",
    response_model=dict,
    summary="Add scrap movies task",
    description="Add tasks to scrap movies",
)
def create_scrap_movies_task(db: Session = Depends(get_db)):
    """
    Create tasks for scraping all movies.
    Sends a Celery task for each movie in the database.
    """
    try:
        from filman_server.database import models

        filmweb_movies = db.query(models.FilmWebMovie).all()
        task_ids = []

        for movie in filmweb_movies:
            celery_task = scrap_movie.delay(schemas.TaskTypes.SCRAP_FILMWEB_MOVIE.value, str(movie.id))
            task_ids.append(celery_task.id)

        logging.info(f"Sent {len(task_ids)} movie scraping tasks to Celery queue")
        return {"status": "success", "tasks_queued": len(task_ids), "celery_task_ids": task_ids}
    except Exception as e:
        logging.error(f"Failed to create movie scraping tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue tasks: {str(e)}")


@tasks_router.get(
    "/new/scrap/filmweb/series",
    response_model=dict,
    summary="Add scrap series task",
    description="Add tasks to scrap series",
)
def create_scrap_series_task(db: Session = Depends(get_db)):
    """
    Create tasks for scraping all series.
    Sends a Celery task for each series in the database.
    """
    try:
        from filman_server.database import models

        filmweb_series = db.query(models.FilmWebSeries).all()
        task_ids = []

        for series in filmweb_series:
            celery_task = scrap_movie.delay(schemas.TaskTypes.SCRAP_FILMWEB_SERIES.value, str(series.id))
            task_ids.append(celery_task.id)

        logging.info(f"Sent {len(task_ids)} series scraping tasks to Celery queue")
        return {"status": "success", "tasks_queued": len(task_ids), "celery_task_ids": task_ids}
    except Exception as e:
        logging.error(f"Failed to create series scraping tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue tasks: {str(e)}")


@tasks_router.get(
    "/new/scrap/filmweb/users/series",
    response_model=dict,
    summary="Add scrap users series task",
    description="Add tasks to scrap users series (watched series)",
)
def create_scrap_users_series_task(db: Session = Depends(get_db)):
    """
    Create tasks for scraping all users' watched series.
    Sends a Celery task for each user with filmweb mapping.
    """
    try:
        from filman_server.database import models

        filmweb_users = db.query(models.FilmWebUserMapping).all()
        task_ids = []

        for user in filmweb_users:
            celery_task = scrap_movie.delay(
                schemas.TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES.value, str(user.filmweb_id)
            )
            task_ids.append(celery_task.id)

        logging.info(f"Sent {len(task_ids)} user series scraping tasks to Celery queue")
        return {"status": "success", "tasks_queued": len(task_ids), "celery_task_ids": task_ids}
    except Exception as e:
        logging.error(f"Failed to create user series scraping tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue tasks: {str(e)}")
