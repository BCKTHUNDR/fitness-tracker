"""Workout repository behavior tests."""

from datetime import date

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
