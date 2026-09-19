"""Application service behavior tests."""

from dataclasses import replace
from datetime import date, datetime

import pytest

from fitness_tracker.database import Database
from fitness_tracker.models import ImageAttachment
from fitness_tracker.repositories.attachment_repository import AttachmentRepository
from fitness_tracker.services.bodyweight_service import BodyweightService
from fitness_tracker.services.inputs import (
	BodyweightDraft,
	ExerciseInput,
	SetInput,
	WorkoutDraft,
)
from fitness_tracker.services.workout_service import WorkoutService


def test_save_workout_persists_draft_with_ordered_children(tmp_path):
	"""Save a complete draft and preserve its exercise and set order."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	service = WorkoutService(database)

	saved = service.save_workout(
		WorkoutDraft(
			workout_date=date(2026, 9, 18),
			exercises=(
				ExerciseInput(
					" Squat ",
					sets=(SetInput(10, 80.0), SetInput(8, 85.0)),
					body_part=" Legs ",
				),
			),
			notes=" Leg day ",
		)
	)

	with database.connection() as connection:
		assert connection.execute("SELECT COUNT(*) FROM workouts").fetchone()[0] == 1
		exercise = connection.execute("SELECT name, body_part FROM exercises").fetchone()
		sets = connection.execute(
			"SELECT set_number, reps, weight FROM exercise_sets ORDER BY set_number"
		).fetchall()

	assert saved.workout_date == date(2026, 9, 18)
	assert tuple(exercise) == ("Squat", "Legs")
	assert [tuple(item) for item in sets] == [(1, 10, 80.0), (2, 8, 85.0)]


def test_save_workout_rolls_back_and_cleans_up_on_mid_save_failure(tmp_path, monkeypatch):
	"""Leave no workout, exercise, or set rows after a save exception."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	service = WorkoutService(database)
	original_add_set = service.repository.add_set

	def fail_after_insert(exercise_set, *, connection=None):
		original_add_set(exercise_set, connection=connection)
		raise RuntimeError("simulated save failure")

	monkeypatch.setattr(service.repository, "add_set", fail_after_insert)

	with pytest.raises(RuntimeError, match="simulated"):
		service.save_workout(
			WorkoutDraft(
				exercises=(ExerciseInput("Squat", sets=(SetInput(5),)),),
			)
		)

	with database.connection() as connection:
		for table in ("workouts", "exercises", "exercise_sets"):
			assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


@pytest.mark.parametrize(
	"draft, message",
	[
		(WorkoutDraft(), "at least one exercise"),
		(WorkoutDraft(exercises=(ExerciseInput(" ", sets=(SetInput(5),)),)), "exercise name"),
		(WorkoutDraft(exercises=(ExerciseInput("Squat"),)), "at least one set"),
		(WorkoutDraft(exercises=(ExerciseInput("Squat", sets=(SetInput(0),)),)), "reps"),
		(WorkoutDraft(exercises=(ExerciseInput("Squat", sets=(SetInput(5, -1),)),)), "weight"),
	],
)
def test_save_workout_rejects_invalid_drafts(tmp_path, draft, message):
	"""Reject invalid drafts before writing any database rows."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()

	with pytest.raises(ValueError, match=message):
		WorkoutService(database).save_workout(draft)

	with database.connection() as connection:
		assert connection.execute("SELECT COUNT(*) FROM workouts").fetchone()[0] == 0


def test_bodyweight_service_defaults_date_and_rejects_invalid_values(tmp_path):
	"""Persist valid bodyweight input and reject invalid measurements."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	service = BodyweightService(database)

	saved = service.save_entry(BodyweightDraft(80.5, notes=" Morning "))
	assert saved.entry_date == datetime.now().astimezone().date()
	assert saved.notes == "Morning"

	for invalid_weight in (0, -1, float("nan"), float("inf")):
		with pytest.raises(ValueError, match="bodyweight"):
			service.save_entry(BodyweightDraft(invalid_weight))


def test_workout_draft_can_update_existing_rows_add_children_and_remove_children(tmp_path):
	"""Edit a loaded draft while preserving retained record IDs."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	service = WorkoutService(database)
	saved = service.save_workout(
		WorkoutDraft(
			workout_date=date(2026, 9, 18),
			exercises=(
				ExerciseInput("Squat", sets=(SetInput(10, 80.0), SetInput(8, 85.0)), body_part="Legs"),
				ExerciseInput("Lunge", sets=(SetInput(10, 20.0),), body_part="Legs"),
			),
			notes="Original",
		)
	)

	draft = service.load_workout_for_edit(saved.id)
	first_exercise = draft.exercises[0]
	first_set = first_exercise.sets[0]
	updated = replace(
		draft,
		workout_date=date(2026, 9, 19),
		notes="Updated",
		exercises=(
			replace(
				first_exercise,
				name="Front Squat",
				sets=(replace(first_set, reps=12), SetInput(6, 90.0)),
			),
		),
	)

	service.save_workout(updated)
	loaded = service.load_workout_for_edit(saved.id)
	assert loaded.workout_date == date(2026, 9, 19)
	assert loaded.notes == "Updated"
	assert len(loaded.exercises) == 1
	assert loaded.exercises[0].name == "Front Squat"
	assert loaded.exercises[0].id == first_exercise.id
	assert [item.reps for item in loaded.exercises[0].sets] == [12, 6]
	assert loaded.exercises[0].sets[0].id == first_set.id


def test_workout_edit_preserves_attachment_metadata(tmp_path):
	"""Keep attachments linked when their owned exercise is edited."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	service = WorkoutService(database)
	saved = service.save_workout(
		WorkoutDraft(exercises=(ExerciseInput("Squat", sets=(SetInput(5),)),))
	)
	draft = service.load_workout_for_edit(saved.id)
	exercise_id = draft.exercises[0].id
	attachment_repository = AttachmentRepository(database)
	attachment = attachment_repository.create(
		ImageAttachment("squat.jpg", "squat.jpg", exercise_id=exercise_id)
	)

	service.save_workout(replace(draft, exercises=(replace(draft.exercises[0], name="Back Squat"),)))

	assert attachment_repository.list_for_owner("exercise_id", exercise_id) == [attachment]


def test_workout_edit_rolls_back_all_changes_on_failure(tmp_path, monkeypatch):
	"""Restore the original workout when an edit fails partway through."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	service = WorkoutService(database)
	saved = service.save_workout(
		WorkoutDraft(exercises=(ExerciseInput("Squat", sets=(SetInput(5),)),), notes="Original")
	)
	draft = service.load_workout_for_edit(saved.id)
	original_update_set = service.repository.update_set

	def fail_after_update(exercise_set, *, connection):
		original_update_set(exercise_set, connection=connection)
		raise RuntimeError("simulated edit failure")

	monkeypatch.setattr(service.repository, "update_set", fail_after_update)
	updated = replace(
		draft,
		notes="Changed",
		exercises=(
			replace(
				draft.exercises[0],
				sets=(replace(draft.exercises[0].sets[0], reps=99),),
			),
		),
	)

	with pytest.raises(RuntimeError, match="simulated"):
		service.save_workout(updated)

	restored = service.load_workout_for_edit(saved.id)
	assert restored.notes == "Original"
	assert restored.exercises[0].sets[0].reps == 5