"""Workout repository behavior tests."""

from datetime import date

import pytest

from fitness_tracker.database import Database
from fitness_tracker.models import Exercise, ExerciseSet, Workout
from fitness_tracker.repositories.workout_repository import WorkoutRepository


def test_workout_exercises_and_sets_preserve_order(tmp_path):
	"""Persist a workout hierarchy and return children in entry order."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = WorkoutRepository(database)
	workout = repository.create_workout(Workout(date(2026, 9, 18)))
	first = repository.add_exercise(Exercise(workout.id, "Squat", 1, "Legs"))
	second = repository.add_exercise(Exercise(workout.id, "Lunge", 2, "Legs"))
	repository.add_set(ExerciseSet(first.id, 2, 8, 80.0))
	repository.add_set(ExerciseSet(first.id, 1, 10, 80.0))

	assert [exercise.id for exercise in repository.list_exercises(workout.id)] == [
		first.id,
		second.id,
	]
	assert [item.set_number for item in repository.list_sets(first.id)] == [1, 2]


def test_workout_history_filters_by_exercise_and_body_part(tmp_path):
	"""Filter workout history through joined exercise attributes."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = WorkoutRepository(database)
	chest_workout = repository.create_workout(Workout(date(2026, 9, 17)))
	legs_workout = repository.create_workout(Workout(date(2026, 9, 18)))
	repository.add_exercise(Exercise(chest_workout.id, "Bench Press", 1, "Chest"))
	repository.add_exercise(Exercise(legs_workout.id, "Squat", 1, "Legs"))

	assert [item.id for item in repository.list_workouts(body_part="Chest")] == [
		chest_workout.id
	]
	assert [item.id for item in repository.list_workouts(exercise_name="Squat")] == [
		legs_workout.id
	]


def test_workout_history_filters_by_inclusive_date_window(tmp_path):
	"""Include workouts on both boundaries of a date window."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = WorkoutRepository(database)
	before = repository.create_workout(Workout(date(2026, 9, 16)))
	start = repository.create_workout(Workout(date(2026, 9, 17)))
	inside = repository.create_workout(Workout(date(2026, 9, 18)))
	end = repository.create_workout(Workout(date(2026, 9, 19)))
	after = repository.create_workout(Workout(date(2026, 9, 20)))

	assert [item.id for item in repository.list_workouts(
		start_date=date(2026, 9, 17),
		end_date=date(2026, 9, 19),
	)] == [start.id, inside.id, end.id]
	assert [item.id for item in repository.list_workouts(
		start_date=date(2026, 9, 18),
	)] == [inside.id, end.id, after.id]
	assert [item.id for item in repository.list_workouts(
		end_date=date(2026, 9, 17),
	)] == [before.id, start.id]


def test_workout_history_rejects_reversed_date_window(tmp_path):
	"""Reject a date range whose start occurs after its end."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = WorkoutRepository(database)

	with pytest.raises(ValueError, match="start_date"):
		repository.list_workouts(
			start_date=date(2026, 9, 19),
			end_date=date(2026, 9, 18),
		)


def test_workout_history_supports_all_sort_fields(tmp_path):
	"""Sort workout history through each supported sort field."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = WorkoutRepository(database)
	legs = repository.create_workout(Workout(date(2026, 9, 18)))
	chest = repository.create_workout(Workout(date(2026, 9, 17)))
	repository.add_exercise(Exercise(legs.id, "Squat", 1, "Legs"))
	repository.add_exercise(Exercise(chest.id, "Bench Press", 1, "Chest"))

	assert [item.id for item in repository.list_workouts(sort_by="date")] == [
		chest.id,
		legs.id,
	]
	assert [item.id for item in repository.list_workouts(sort_by="exercise_name")] == [
		chest.id,
		legs.id,
	]
	assert [item.id for item in repository.list_workouts(sort_by="body_part")] == [
		chest.id,
		legs.id,
	]
	assert [item.id for item in repository.list_workouts(sort_by="weekday")] == [
		chest.id,
		legs.id,
	]


def test_workout_history_rejects_invalid_sort_and_weekday(tmp_path):
	"""Reject unsupported sorting and weekday values."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = WorkoutRepository(database)

	with pytest.raises(ValueError, match="sort field"):
		repository.list_workouts(sort_by="created_at")
	with pytest.raises(ValueError, match="weekday"):
		repository.list_workouts(weekday=7)


def test_workout_persists_after_database_reopen(tmp_path):
	"""Return saved workouts after creating a fresh database object."""
	database_path = tmp_path / "fitness.sqlite3"
	database = Database(database_path)
	database.initialize()
	repository = WorkoutRepository(database)
	saved = repository.create_workout(Workout(date(2026, 9, 18), "Recovery"))

	reopened_repository = WorkoutRepository(Database(database_path))
	assert reopened_repository.get_workout(saved.id) == saved
