import os
from alembic import command
from alembic.config import Config

from .db import SQLALCHEMY_DATABASE_URL


def _discover_paths() -> tuple[str, str]:
    """Locate migrations directory and alembic.ini.

    Order of precedence:
      1. Env vars MIGRATIONS_PATH / ALEMBIC_INI
      2. Sibling of project root discovered by ascending from this file
      3. Common fallbacks: /app/migrations, /migrations
    """
    env_migrations = os.environ.get("MIGRATIONS_PATH")
    env_ini = os.environ.get("ALEMBIC_INI")
    if env_migrations and env_ini:
        return env_migrations, env_ini

    # ascend from current file looking for alembic.ini + migrations
    start = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    current = start
    while True:
        cand_ini = os.path.join(current, "alembic.ini")
        cand_mig = os.path.join(current, "migrations")
        if os.path.isfile(cand_ini) and os.path.isdir(cand_mig):
            return cand_mig, cand_ini
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    # Fallback candidates commonly used in containers
    for base in ("/app", "/"):
        cand_ini = os.path.join(base, "alembic.ini")
        cand_mig = os.path.join(base, "migrations")
        if os.path.isfile(cand_ini) and os.path.isdir(cand_mig):
            return cand_mig, cand_ini

    raise FileNotFoundError(
        "Could not locate migrations and alembic.ini. Set MIGRATIONS_PATH and ALEMBIC_INI env vars or ensure they are mounted. "
        f"Checked start={start} and fallbacks /app,/"
    )


def run_migrations():
    """Run Alembic migrations up to head using discovered paths.

    Safe to call multiple times (Alembic tracks current head).
    """
    migrations_path, ini_path = _discover_paths()
    cfg = Config(ini_path)
    cfg.set_main_option("script_location", migrations_path)
    cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    command.upgrade(cfg, "head")


def trigger_migrations():
    """Conditionally run migrations based on env variable.

    Called after all models are imported to prevent circular import issues.
    """
    if os.environ.get("RUN_MIGRATIONS_ON_STARTUP", "1") != "1":
        return
    try:
        run_migrations()
    except Exception as e:  # pragma: no cover
        print(f"[migrations] Skipped (reason: {e})")
