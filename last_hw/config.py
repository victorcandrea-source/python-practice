"""
Configuration management for the Task Management System.
Reads database credentials from environment variables.
"""

import os
from typing import Optional


class Config:
    """Application configuration class."""

    # Database configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "task_management")

    @classmethod
    def get_database_url(cls) -> str:
        """Construct PostgreSQL connection string."""
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@"
            f"{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def get_database_url_psycopg2(cls) -> str:
        """Construct psycopg2 connection string."""
        return (
            f"host={cls.DB_HOST} port={cls.DB_PORT} "
            f"user={cls.DB_USER} password={cls.DB_PASSWORD} "
            f"dbname={cls.DB_NAME}"
        )


# Application settings
APP_TITLE = "Task Management System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A production-ready task management API with PostgreSQL backend"
