"""Persistence operations for workouts, exercises, and exercise sets."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from fitness_tracker.database import Database
from fitness_tracker.models import Exercise, ExerciseSet, Workout


class WorkoutRepository:
	"""Persist workout records and their ordered exercise data."""

	def __init__(self, database: Database) -> None:
		"""Store the database dependency used by this repository."""
		self.database = database

	def create_workout(self, workout: Workout) -> Workout:
		"""Insert a workout and return it with its generated ID."""
		with self.database.connection() as connection:
			cursor = connection.execute(
				"INSERT INTO workouts(workout_date, notes) VALUES (?, ?)",
				(workout.workout_date.isoformat(), workout.notes),
			)
			return Workout(
				id=cursor.lastrowid,
				workout_date=workout.workout_date,
				notes=workout.notes,
			)

	def get_workout(self, workout_id: int) -> Workout | None:
		"""Return one workout by ID or None when it does not exist."""
		with self.database.connection() as connection:
			row = connection.execute(
				"SELECT id, workout_date, notes FROM workouts WHERE id = ?",
				(workout_id,),
			).fetchone()
		return Workout.from_row(row) if row else None

	def list_workouts(
		self,
		*,
		exercise_name: str | None = None,
		body_part: str | None = None,
		weekday: int | None = None,
		start_date: date | None = None,
		end_date: date | None = None,
		sort_by: str = "date",
	) -> list[Workout]:
		"""List workouts using optional filters and an allowlisted sort field."""
		sort_columns = {
			"date": "w.workout_date",
			"exercise_name": "MIN(e.name)",
			"body_part": "MIN(e.body_part)",
			"weekday": "strftime('%w', w.workout_date)",
		}
		if sort_by not in sort_columns:
			raise ValueError(f"Unsupported workout sort field: {sort_by}")

		clauses: list[str] = []
		parameters: list[object] = []
		if exercise_name:
			clauses.append("e.name = ?")
			parameters.append(exercise_name)
		if body_part:
			clauses.append("e.body_part = ?")
			parameters.append(body_part)
		if weekday is not None:
			if not 0 <= weekday <= 6:
				raise ValueError("weekday must be between 0 and 6")
			clauses.append("CAST(strftime('%w', w.workout_date) AS INTEGER) = ?")
			parameters.append(weekday)
		if start_date and end_date and start_date > end_date:
			raise ValueError("start_date must be on or before end_date")
		if start_date:
			clauses.append("w.workout_date >= ?")
			parameters.append(start_date.isoformat())
		if end_date:
			clauses.append("w.workout_date <= ?")
			parameters.append(end_date.isoformat())

		where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
		query = f"""
			SELECT w.id, w.workout_date, w.notes
			FROM workouts AS w
			LEFT JOIN exercises AS e ON e.workout_id = w.id
			{where_clause}
			GROUP BY w.id
			ORDER BY {sort_columns[sort_by]}, w.id
		"""
		with self.database.connection() as connection:
			rows = connection.execute(query, parameters).fetchall()
		return [Workout.from_row(row) for row in rows]

	def add_exercise(self, exercise: Exercise) -> Exercise:
		"""Insert an exercise occurrence and return it with its generated ID."""
		with self.database.connection() as connection:
			cursor = connection.execute(
				"""INSERT INTO exercises
				   (workout_id, name, body_part, notes, position)
				   VALUES (?, ?, ?, ?, ?)""",
				(
					exercise.workout_id,
					exercise.name,
					exercise.body_part,
					exercise.notes,
					exercise.position,
				),
			)
		return replace(exercise, id=cursor.lastrowid)

	def add_set(self, exercise_set: ExerciseSet) -> ExerciseSet:
		"""Insert one exercise set and return it with its generated ID."""
		with self.database.connection() as connection:
			cursor = connection.execute(
				"""INSERT INTO exercise_sets
				   (exercise_id, set_number, reps, weight, notes)
				   VALUES (?, ?, ?, ?, ?)""",
				(
					exercise_set.exercise_id,
					exercise_set.set_number,
					exercise_set.reps,
					exercise_set.weight,
					exercise_set.notes,
				),
			)
		return replace(exercise_set, id=cursor.lastrowid)

	def list_exercises(self, workout_id: int) -> list[Exercise]:
		"""Return a workout's exercises in entry order."""
		with self.database.connection() as connection:
			rows = connection.execute(
				"""SELECT id, workout_id, name, body_part, notes, position
				   FROM exercises WHERE workout_id = ? ORDER BY position""",
				(workout_id,),
			).fetchall()
		return [Exercise(**dict(row)) for row in rows]

	def list_sets(self, exercise_id: int) -> list[ExerciseSet]:
		"""Return an exercise's sets in set-number order."""
		with self.database.connection() as connection:
			rows = connection.execute(
				"""SELECT id, exercise_id, set_number, reps, weight, notes
				   FROM exercise_sets WHERE exercise_id = ? ORDER BY set_number""",
				(exercise_id,),
			).fetchall()
		return [ExerciseSet(**dict(row)) for row in rows]
