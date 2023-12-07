import sqlite3
import uvicorn
import mysql.connector
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from watched import WatchedManager
from users import UserManager

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/user/create")
async def create_user(id_filmweb: str, id_discord: int):
    user_manager = UserManager()
    result = user_manager.create_user(id_filmweb, id_discord)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/user/delete")
async def delete_user(id_filmweb: str):
    user_manager = UserManager()
    if user_manager.delete_user(id_filmweb):
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/user/watched/film/add")
async def add_movie(
    id_filmweb: str,
    movie_id: int,
    rate: int,
    comment: str,
    favourite: bool,
    unix_timestamp: int,
):
    watched_manager = WatchedManager()
    result = watched_manager.add_watched_movie(
        id_filmweb, movie_id, rate, comment, favourite, unix_timestamp
    )

    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/user/watched/film/all")
async def get_all_watched_movie(id_filmweb: str):
    watched_manager = WatchedManager()
    result = watched_manager.get_all_watched_movie(id_filmweb)
    if result is None:
        raise HTTPException(status_code=500, detail="No movies found")
    else:
        return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
