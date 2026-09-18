"""Bodyweight repository behavior tests."""

from datetime import date

from fitness_tracker.database import Database
from fitness_tracker.models import BodyweightEntry, ImageAttachment
from fitness_tracker.repositories.attachment_repository import AttachmentRepository
from fitness_tracker.repositories.bodyweight_repository import BodyweightRepository


def test_bodyweight_entries_are_independent_and_newest_first(tmp_path):
	"""Persist bodyweight entries independently from workout records."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	repository = BodyweightRepository(database)
	older = repository.create(BodyweightEntry(date(2026, 9, 17), 81.0))
	newer = repository.create(BodyweightEntry(date(2026, 9, 18), 80.5))

	assert [entry.id for entry in repository.list_entries()] == [newer.id, older.id]


def test_bodyweight_attachment_round_trips_metadata(tmp_path):
	"""Persist and retrieve an attachment owned by a bodyweight entry."""
	database = Database(tmp_path / "fitness.sqlite3")
	database.initialize()
	bodyweight = BodyweightRepository(database).create(
		BodyweightEntry(date(2026, 9, 18), 80.5)
	)
	repository = AttachmentRepository(database)
	attachment = repository.create(
		ImageAttachment("stored.jpg", "original.jpg", "image/jpeg", bodyweight_id=bodyweight.id)
	)

	assert repository.list_for_owner("bodyweight_id", bodyweight.id) == [attachment]
