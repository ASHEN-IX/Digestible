import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
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


def run_migrations_online():
    """Run migrations in 'online' mode"""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


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
