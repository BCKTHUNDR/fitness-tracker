"""Persistence operations for image attachment metadata."""

from __future__ import annotations

from dataclasses import replace

from fitness_tracker.database import Database
from fitness_tracker.models import ImageAttachment


class AttachmentRepository:
    """Persist image metadata while files remain in local storage."""

    def __init__(self, database: Database) -> None:
        """Store the database dependency used by this repository."""
        self.database = database

    def create(self, attachment: ImageAttachment) -> ImageAttachment:
        """Insert one attachment and return it with its generated ID."""
        owner_count = sum(
            owner is not None
            for owner in (
                attachment.workout_id,
                attachment.exercise_id,
                attachment.bodyweight_id,
            )
        )
        if owner_count != 1:
            raise ValueError("an attachment must have exactly one owner")

        with self.database.connection() as connection:
            cursor = connection.execute(
                """INSERT INTO image_attachments
                   (workout_id, exercise_id, bodyweight_id, file_name,
                    original_name, mime_type)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    attachment.workout_id,
                    attachment.exercise_id,
                    attachment.bodyweight_id,
                    attachment.file_name,
                    attachment.original_name,
                    attachment.mime_type,
                ),
            )
        return replace(attachment, id=cursor.lastrowid)

    def list_for_owner(self, owner_column: str, owner_id: int) -> list[ImageAttachment]:
        """Return attachments for one allowlisted owner column."""
        owner_columns = {"workout_id", "exercise_id", "bodyweight_id"}
        if owner_column not in owner_columns:
            raise ValueError(f"Unsupported attachment owner: {owner_column}")

        with self.database.connection() as connection:
            rows = connection.execute(
                f"""SELECT id, file_name, original_name, mime_type,
                          workout_id, exercise_id, bodyweight_id
                    FROM image_attachments WHERE {owner_column} = ?
                    ORDER BY id""",
                (owner_id,),
            ).fetchall()
        return [ImageAttachment(**dict(row)) for row in rows]