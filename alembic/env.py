import asyncio
import sys
import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context

# Add backend to path
sys.path.insert(0, "/app")

# Import models and config
from backend.database import Base
from backend.config import get_settings

# Alembic Config object
config = context.config
settings = get_settings()

# Setup logging
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        pass  # Skip if logging config missing

# Set target metadata
target_metadata = Base.metadata

# Set database URL from settings to override alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)
config.set_main_option("sqlalchemy.url", settings.database_url)


def do_run_migrations(connection):
    """Run migrations in 'online' mode"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations using async engine"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Entry point for online migrations"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    # Offline mode (SQL script generation)
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
else:
    # Online mode
    run_migrations_online()
