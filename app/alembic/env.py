import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Make sure Python can find database.py and models.py (they live in /code,
# the same folder alembic.ini is in)
sys.path.append(os.getcwd())

from database import Base
import models  # noqa: F401 -- imported so its tables register with Base

# this is the Alembic Config object
config = context.config

# Override the database URL with the one from our environment variable,
# instead of whatever placeholder is in alembic.ini
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL", "postgresql://alemeno:alemeno_pass@postgres:5432/transactions_db"),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This tells Alembic's "autogenerate" feature what your tables SHOULD look like
target_metadata = Base.metadata


def run_migrations_offline() -> None:
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