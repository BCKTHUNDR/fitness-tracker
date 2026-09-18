"""Persistence operations for independent bodyweight entries."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from fitness_tracker.database import Database
from fitness_tracker.models import BodyweightEntry


class BodyweightRepository:
	"""Persist and query bodyweight records independently from workouts."""

	def __init__(self, database: Database) -> None:
		"""Store the database dependency used by this repository."""
		self.database = database

	def create(self, entry: BodyweightEntry) -> BodyweightEntry:
		"""Insert a bodyweight entry and return it with its generated ID."""
		with self.database.connection() as connection:
			cursor = connection.execute(
				"""INSERT INTO bodyweight_entries(entry_date, weight, notes)
				   VALUES (?, ?, ?)""",
				(entry.entry_date.isoformat(), entry.weight, entry.notes),
			)
		return replace(entry, id=cursor.lastrowid)

	def list_entries(self) -> list[BodyweightEntry]:
		"""Return bodyweight entries ordered from newest to oldest."""
		with self.database.connection() as connection:
			rows = connection.execute(
				"""SELECT id, entry_date, weight, notes
				   FROM bodyweight_entries ORDER BY entry_date DESC, id DESC"""
			).fetchall()
		return [
			BodyweightEntry(
				id=row["id"],
				entry_date=date.fromisoformat(row["entry_date"]),
				weight=row["weight"],
				notes=row["notes"],
			)
			for row in rows
		]
