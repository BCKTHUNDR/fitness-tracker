"""Validated workout creation use cases."""

from __future__ import annotations

import math
from dataclasses import replace
from datetime import datetime
from logging import getLogger

from fitness_tracker.database import Database
from fitness_tracker.models import Exercise, ExerciseSet, Workout
from fitness_tracker.repositories.workout_repository import WorkoutRepository
from fitness_tracker.services.inputs import ExerciseInput, SetInput, WorkoutDraft

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
		if draft.id is not None:
			return self._update_workout(draft)
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

	def load_workout_for_edit(self, workout_id: int) -> WorkoutDraft:
		"""Load a persisted workout and its children into an editable draft."""
		workout = self.repository.get_workout(workout_id)
		if workout is None:
			raise ValueError(f"workout {workout_id} does not exist")

		exercises = []
		for exercise in self.repository.list_exercises(workout_id):
			exercises.append(
				ExerciseInput(
					name=exercise.name,
					sets=tuple(
						SetInput(
							reps=exercise_set.reps,
							weight=exercise_set.weight,
							notes=exercise_set.notes,
							id=exercise_set.id,
						)
						for exercise_set in self.repository.list_sets(exercise.id)
					),
					body_part=exercise.body_part,
					notes=exercise.notes,
					id=exercise.id,
				)
			)
		return WorkoutDraft(
			workout_date=workout.workout_date,
			exercises=tuple(exercises),
			notes=workout.notes,
			id=workout.id,
		)

	def _update_workout(self, draft: WorkoutDraft) -> Workout:
		"""Update retained rows and synchronize added or removed children."""
		workout = self.repository.get_workout(draft.id)
		if workout is None:
			raise ValueError(f"workout {draft.id} does not exist")
		existing_exercises = {
			exercise.id: exercise
			for exercise in self.repository.list_exercises(draft.id)
		}
		existing_sets = {
			exercise.id: {
				exercise_set.id: exercise_set
				for exercise_set in self.repository.list_sets(exercise.id)
			}
			for exercise in existing_exercises.values()
		}
		self._validate_existing_ids(draft, existing_exercises, existing_sets)

		with self.database.connection() as connection:
			self.repository.update_workout(
				Workout(
					draft.workout_date or datetime.now().astimezone().date(),
					self._optional_text(draft.notes),
					draft.id,
				),
				connection=connection,
			)
			retained_exercise_ids = {item.id for item in draft.exercises if item.id is not None}
			for exercise_id in existing_exercises:
				if exercise_id not in retained_exercise_ids:
					self.repository.delete_exercise(exercise_id, connection=connection)

			persisted_exercises = []
			for position, exercise_input in enumerate(draft.exercises, start=1):
				exercise = Exercise(
					draft.id,
					exercise_input.name.strip(),
					1_000_000 + position,
					self._optional_text(exercise_input.body_part),
					self._optional_text(exercise_input.notes),
					exercise_input.id,
				)
				if exercise.id is None:
					exercise = self.repository.add_exercise(exercise, connection=connection)
				else:
					self.repository.update_exercise(exercise, connection=connection)
				persisted_exercises.append((position, exercise, exercise_input))

			persisted_sets = []
			for _, exercise, exercise_input in persisted_exercises:
				retained_set_ids = {item.id for item in exercise_input.sets if item.id is not None}
				for set_id in existing_sets.get(exercise.id, {}):
					if set_id not in retained_set_ids:
						self.repository.delete_set(set_id, connection=connection)
				for set_number, set_input in enumerate(exercise_input.sets, start=1):
					set_record = ExerciseSet(
						exercise.id,
						1_000_000 + set_number,
						set_input.reps,
						set_input.weight,
						self._optional_text(set_input.notes),
						set_input.id,
					)
					if set_record.id is None:
						set_record = self.repository.add_set(set_record, connection=connection)
					else:
						self.repository.update_set(set_record, connection=connection)
					persisted_sets.append((set_number, set_record))

			for position, exercise, _ in persisted_exercises:
				self.repository.update_exercise(
					replace(exercise, position=position),
					connection=connection,
				)
			for set_number, set_record in persisted_sets:
				self.repository.update_set(
					replace(set_record, set_number=set_number),
					connection=connection,
				)

		return Workout(
			draft.workout_date or datetime.now().astimezone().date(),
			self._optional_text(draft.notes),
			draft.id,
		)

	def _validate_existing_ids(self, draft, existing_exercises, existing_sets) -> None:
		"""Reject duplicate or unrelated IDs in an edit draft."""
		exercise_ids = [item.id for item in draft.exercises if item.id is not None]
		if len(exercise_ids) != len(set(exercise_ids)) or not set(exercise_ids) <= set(existing_exercises):
			raise ValueError("draft contains an invalid or duplicate exercise ID")
		set_ids = []
		for exercise in draft.exercises:
			for set_input in exercise.sets:
				if set_input.id is not None:
					set_ids.append(set_input.id)
					if set_input.id not in existing_sets.get(exercise.id, {}):
						raise ValueError("draft contains a set ID for the wrong exercise")
		if len(set_ids) != len(set(set_ids)):
			raise ValueError("draft contains a duplicate set ID")


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
