from __future__ import annotations

import sqlite3

from fitness_tracker.database import Database


def test_initialize_creates_schema_and_is_idempotent(tmp_path):
    database = Database(tmp_path / "fitness.sqlite3")

    database.initialize()
    database.initialize()

    with database.connection() as connection:
        assert connection.execute(
            "SELECT version FROM schema_version"
        ).fetchone()[0] == 1
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {
            "workouts",
            "exercises",
            "exercise_sets",
            "bodyweight_entries",
            "image_attachments",
        } <= tables


def test_foreign_keys_and_attachment_owner_constraint_are_enforced(tmp_path):
    database = Database(tmp_path / "fitness.sqlite3")
    database.initialize()

    with database.connection() as connection:
        try:
            connection.execute(
                "INSERT INTO image_attachments "
                "(file_name, original_name) VALUES (?, ?)",
                ("stored.jpg", "original.jpg"),
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("an attachment must have exactly one owner")

        try:
            connection.execute(
                "INSERT INTO exercises(workout_id, name, position) "
                "VALUES (?, ?, ?)",
                (999, "Bench Press", 1),
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("foreign keys must be enabled")
