import logging
import os
import sys

from fastapi.responses import JSONResponse
import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from filman_server.cron import Cron
from filman_server.database import models
from filman_server.database.migrate import trigger_migrations
from filman_server.database.db import engine
from filman_server.routes import discord, filmweb, tasks, users, utils

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logging.getLogger("uvicorn").setLevel(LOG_LEVEL)
logging.getLogger("uvicorn.access").setLevel(LOG_LEVEL)
logging.getLogger("fastapi").setLevel(LOG_LEVEL)

if os.environ.get("SENTRY_ENABLED", "false") == "true":
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        enable_tracing=True,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
    )

trigger_migrations()
models.Base.metadata.create_all(bind=engine)

cron = Cron()
app = FastAPI()

app.include_router(users.users_router)
app.include_router(discord.discord_router)
app.include_router(filmweb.filmweb_router)
app.include_router(tasks.tasks_router)
app.include_router(utils.utils_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    if response.status_code >= 400:
        logging.warning(f"{request.method} {request.url.path} -> {response.status_code}")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    logging.info("Filman server started")
    cron.start()
    logging.debug("cron running")
    uvicorn.run(app, host="0.0.0.0", port=8000)
