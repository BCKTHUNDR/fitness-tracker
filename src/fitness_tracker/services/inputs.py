"""In-memory input objects used before records are persisted."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True, slots=True)
class SetInput:
	"""Capture one set before its parent exercise is saved."""

	reps: int
	weight: float | None = None
	notes: str | None = None


@dataclass(frozen=True, slots=True)
class ExerciseInput:
	"""Capture an exercise and its sets before a workout is saved."""

	name: str
	sets: tuple[SetInput, ...] = field(default_factory=tuple)
	body_part: str | None = None
	notes: str | None = None


@dataclass(frozen=True, slots=True)
class WorkoutDraft:
	"""Capture a complete workout without creating database rows."""

	workout_date: date | None = None
	exercises: tuple[ExerciseInput, ...] = field(default_factory=tuple)
	notes: str | None = None


@dataclass(frozen=True, slots=True)
class BodyweightDraft:
	"""Capture a bodyweight entry before it is persisted."""

	weight: float
	entry_date: date | None = None
	notes: str | None = None