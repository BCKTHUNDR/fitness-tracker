"""SQLite connection and schema management for the fitness tracker."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION = 1

_SCHEMA_MIGRATIONS: dict[int, str] = {
    1: """
    CREATE TABLE workouts (
        id INTEGER PRIMARY KEY,
        workout_date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE exercises (
        id INTEGER PRIMARY KEY,
        workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        body_part TEXT,
        notes TEXT,
        position INTEGER NOT NULL CHECK (position > 0),
        UNIQUE (workout_id, position)
    );

    CREATE TABLE exercise_sets (
        id INTEGER PRIMARY KEY,
        exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
        set_number INTEGER NOT NULL CHECK (set_number > 0),
        reps INTEGER NOT NULL CHECK (reps > 0),
        weight REAL CHECK (weight IS NULL OR weight >= 0),
        notes TEXT,
        UNIQUE (exercise_id, set_number)
    );

    CREATE TABLE bodyweight_entries (
        id INTEGER PRIMARY KEY,
        entry_date TEXT NOT NULL,
        weight REAL NOT NULL CHECK (weight > 0),
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE image_attachments (
        id INTEGER PRIMARY KEY,
        workout_id INTEGER REFERENCES workouts(id) ON DELETE CASCADE,
        exercise_id INTEGER REFERENCES exercises(id) ON DELETE CASCADE,
        bodyweight_id INTEGER REFERENCES bodyweight_entries(id) ON DELETE CASCADE,
        file_name TEXT NOT NULL,
        original_name TEXT NOT NULL,
        mime_type TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CHECK (
            (workout_id IS NOT NULL) +
            (exercise_id IS NOT NULL) +
            (bodyweight_id IS NOT NULL) = 1
        )
    );

    CREATE INDEX idx_workouts_date ON workouts(workout_date);
    CREATE INDEX idx_exercises_name ON exercises(name);
    CREATE INDEX idx_exercises_body_part ON exercises(body_part);
    CREATE INDEX idx_exercises_workout ON exercises(workout_id);
    CREATE INDEX idx_sets_exercise ON exercise_sets(exercise_id, set_number);
    CREATE INDEX idx_bodyweight_date ON bodyweight_entries(entry_date);
    CREATE INDEX idx_attachments_workout ON image_attachments(workout_id);
    CREATE INDEX idx_attachments_exercise ON image_attachments(exercise_id);
    CREATE INDEX idx_attachments_bodyweight ON image_attachments(bodyweight_id);
    """
}


class Database:
    """Manage SQLite connections and apply schema migrations."""

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        """Create the database and apply any migrations not yet installed."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_version "
                "(version INTEGER NOT NULL)"
            )
            current_version = connection.execute(
                "SELECT version FROM schema_version LIMIT 1"
            ).fetchone()
            installed_version = current_version[0] if current_version else 0

            for version in range(installed_version + 1, SCHEMA_VERSION + 1):
                connection.executescript(_SCHEMA_MIGRATIONS[version])
                connection.execute("DELETE FROM schema_version")
                connection.execute(
                    "INSERT INTO schema_version(version) VALUES (?)", (version,)
                )

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a configured connection and commit successful operations."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
