import uvicorn
import sentry_sdk

from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from typing import Optional, List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from filman_server.database import crud, models, schemas
from filman_server.database.db import SessionLocal, engine

from filman_server.routes import users, discord, filmweb, tasks

models.Base.metadata.create_all(bind=engine)

sentry_sdk.init(
    dsn="https://e90f28bf688cd7f8a1f8dcbc3586d359@o4506423653105664.ingest.sentry.io/4506423687774208",
    enable_tracing=True,
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
)

app = FastAPI()

app.include_router(users.users_router)
app.include_router(discord.discord_router)
app.include_router(filmweb.filmweb_router)
app.include_router(tasks.tasks_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.run(app, host="localhost", port=8000)
