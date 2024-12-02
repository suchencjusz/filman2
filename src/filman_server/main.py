import logging
import os
import sys

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from filman_server.cron import Cron
from filman_server.database import models
from filman_server.database.db import engine
from filman_server.routes import discord, filmweb, tasks, users

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logging.getLogger("uvicorn").setLevel(LOG_LEVEL)
logging.getLogger("uvicorn.access").setLevel(LOG_LEVEL)

if os.environ.get("SENTRY_ENABLED", "false") == "true":
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        enable_tracing=True,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
    )

models.Base.metadata.create_all(bind=engine)

cron = Cron()
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
    logging.info("Filman server started")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    logging.debug("uvicorn running")
    cron.start()
    logging.debug("cron running")
