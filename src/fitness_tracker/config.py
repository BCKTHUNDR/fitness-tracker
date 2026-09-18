"""Application paths and configuration defaults."""

from __future__ import annotations

import os
from pathlib import Path

APPLICATION_DIRECTORY_NAME = "fitness-tracker"
DATABASE_FILE_NAME = "fitness.sqlite3"
ATTACHMENTS_DIRECTORY_NAME = "attachments"


def application_data_directory() -> Path:
    """Return the per-user directory used for local application data."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    base_directory = Path(local_app_data) if local_app_data else Path.home() / ".local" / "share"
    return base_directory / APPLICATION_DIRECTORY_NAME


def database_path() -> Path:
    """Return the default SQLite database path."""
    return application_data_directory() / DATABASE_FILE_NAME


def attachments_directory() -> Path:
    """Return the default directory for copied image attachments."""
    return application_data_directory() / ATTACHMENTS_DIRECTORY_NAME
