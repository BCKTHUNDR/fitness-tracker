"""Small domain value objects shared by application layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TypeVar

from typing_extensions import Self

WorkoutType = TypeVar("WorkoutType", bound="Workout")


@dataclass(frozen=True, slots=True)
class Workout:
    """Represent a saved workout."""

    workout_date: date
    notes: str | None = None
    id: int | None = None

    @classmethod
    def from_row(cls, row) -> Self:
        """Build a workout from a SQLite row."""
        return cls(
            id=row["id"],
            workout_date=date.fromisoformat(row["workout_date"]),
            notes=row["notes"],
        )


@dataclass(frozen=True, slots=True)
class Exercise:
    """Represent an exercise occurrence within a workout."""

    workout_id: int
    name: str
    position: int
    body_part: str | None = None
    notes: str | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class ExerciseSet:
    """Represent one ordered set for an exercise occurrence."""

    exercise_id: int
    set_number: int
    reps: int
    weight: float | None = None
    notes: str | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class BodyweightEntry:
    """Represent a bodyweight measurement independent of any workout."""

    entry_date: date
    weight: float
    notes: str | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class ImageAttachment:
    """Represent metadata for a locally stored image attachment."""

    file_name: str
    original_name: str
    mime_type: str | None = None
    workout_id: int | None = None
    exercise_id: int | None = None
    bodyweight_id: int | None = None
    id: int | None = None
