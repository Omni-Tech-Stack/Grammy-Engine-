"""
Database migration runner for Railway deployment
"""
import os
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run pending database migrations"""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    command.upgrade(alembic_cfg, "head")
    print("✅ Migrations completed successfully")

if __name__ == "__main__":
    run_migrations()
