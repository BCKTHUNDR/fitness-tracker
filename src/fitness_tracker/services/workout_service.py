"""Validated workout creation use cases."""

from __future__ import annotations

import math
from datetime import datetime
from logging import getLogger

from fitness_tracker.database import Database
from fitness_tracker.models import Exercise, ExerciseSet, Workout
from fitness_tracker.repositories.workout_repository import WorkoutRepository
from fitness_tracker.services.inputs import WorkoutDraft

logger = getLogger(__name__)


class WorkoutService:
	"""Validate and atomically persist complete workout drafts."""

	def __init__(self, database: Database) -> None:
		"""Store the database and repository dependencies."""
		self.database = database
		self.repository = WorkoutRepository(database)

	def save_workout(self, draft: WorkoutDraft) -> Workout:
		"""Validate and save a draft without leaving partial records."""
		self._validate_draft(draft)
		saved_workout: Workout | None = None
		try:
			with self.database.connection() as connection:
				saved_workout = self.repository.create_workout(
					Workout(
						draft.workout_date or datetime.now().astimezone().date(),
						self._optional_text(draft.notes),
					),
					connection=connection,
				)
				for position, exercise_input in enumerate(draft.exercises, start=1):
					saved_exercise = self.repository.add_exercise(
						Exercise(
							saved_workout.id,
							exercise_input.name.strip(),
							position,
							self._optional_text(exercise_input.body_part),
							self._optional_text(exercise_input.notes),
						),
						connection=connection,
					)
					for set_number, set_input in enumerate(exercise_input.sets, start=1):
						self.repository.add_set(
							ExerciseSet(
								saved_exercise.id,
								set_number,
								set_input.reps,
								set_input.weight,
								self._optional_text(set_input.notes),
							),
							connection=connection,
						)
		except Exception:
			if saved_workout and saved_workout.id is not None:
				try:
					self.repository.delete_workout(saved_workout.id)
				except Exception:
					logger.exception(
						"Failed to clean up workout %s after save failure",
						saved_workout.id,
					)
			raise
		return saved_workout

	def _validate_draft(self, draft: WorkoutDraft) -> None:
		"""Reject invalid workout input before opening a transaction."""
		if not draft.exercises:
			raise ValueError("a workout must contain at least one exercise")
		for exercise in draft.exercises:
			if not exercise.name.strip():
				raise ValueError("exercise name cannot be blank")
			if not exercise.sets:
				raise ValueError("each exercise must contain at least one set")
			for exercise_set in exercise.sets:
				if not isinstance(exercise_set.reps, int) or isinstance(exercise_set.reps, bool) or exercise_set.reps <= 0:
					raise ValueError("reps must be a positive integer")
				if exercise_set.weight is not None and (
					isinstance(exercise_set.weight, bool)
					or not isinstance(exercise_set.weight, (int, float))
					or not math.isfinite(exercise_set.weight)
					or exercise_set.weight < 0
				):
					raise ValueError("weight must be a finite non-negative number")

	def _optional_text(self, value: str | None) -> str | None:
		"""Normalize optional text fields to None when blank."""
		return value.strip() if value and value.strip() else None
