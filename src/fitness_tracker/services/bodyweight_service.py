"""Validated bodyweight entry use cases."""

from __future__ import annotations

import math
from datetime import datetime

from fitness_tracker.database import Database
from fitness_tracker.models import BodyweightEntry
from fitness_tracker.repositories.bodyweight_repository import BodyweightRepository
from fitness_tracker.services.inputs import BodyweightDraft


class BodyweightService:
	"""Validate and persist independent bodyweight drafts."""

	def __init__(self, database: Database) -> None:
		"""Store the database and repository dependencies."""
		self.repository = BodyweightRepository(database)

	def save_entry(self, draft: BodyweightDraft) -> BodyweightEntry:
		"""Validate and save a bodyweight draft using today's date by default."""
		if (
			isinstance(draft.weight, bool)
			or not isinstance(draft.weight, (int, float))
			or not math.isfinite(draft.weight)
			or draft.weight <= 0
		):
			raise ValueError("bodyweight must be a finite positive number")
		return self.repository.create(
			BodyweightEntry(
				entry_date=draft.entry_date or datetime.now().astimezone().date(),
				weight=draft.weight,
				notes=draft.notes.strip() if draft.notes and draft.notes.strip() else None,
			)
		)
