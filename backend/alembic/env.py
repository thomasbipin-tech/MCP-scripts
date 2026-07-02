"""Alembic environment.

Reads the database URL from the ``DATABASE_URL`` env var (same variable the
app itself uses, see ``app/core/config.py``) rather than from
``alembic.ini``, so the identical config works in Docker Compose, CI, and
local dev. Autogenerate is wired to ``app.db.base:Base`` — import errors are
tolerated (the module may not exist yet / may not have models registered),
since a bare Alembic scaffold with no authored migrations should still be
runnable for `alembic history` / `alembic current`.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make the `app` package importable when Alembic is invoked from `backend/`
# (matches the convention in backend/conftest.py).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# This is the Alembic Config object, which provides access to values within
# the .ini file in use.
config = context.config

# Interpret the config file for Python logging, unless it's disabled.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# DATABASE_URL is the single source of truth for the connection string.
# Falls back to the same SQLite dev default as app/core/config.py so the
# scaffold is runnable with nothing provisioned.
database_url = os.getenv("DATABASE_URL", "sqlite:///./dealproof.db")
config.set_main_option("sqlalchemy.url", database_url)

# target_metadata drives autogenerate (`alembic revision --autogenerate`).
# app.db.base:Base is where models register their tables (see app/models);
# tolerate it not being importable yet so the scaffold works before that
# module exists / before models are wired up.
try:
    from app.db.base import Base  # noqa: E402

    target_metadata = Base.metadata
except Exception:  # pragma: no cover - scaffold fallback
    target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an
    Engine is acceptable here as well. By skipping the Engine creation we
    don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
