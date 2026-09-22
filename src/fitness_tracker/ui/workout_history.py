"""Workout history and workout detail views."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from fitness_tracker.models import Workout
from fitness_tracker.repositories.workout_repository import WorkoutRepository


class WorkoutHistoryFrame(ttk.Frame):
	"""Display filterable workouts and the selected workout details."""

	def __init__(self, parent: tk.Misc, repository: WorkoutRepository, on_new=None, on_edit=None) -> None:
		"""Build the history filters, results table, and detail panel."""
		super().__init__(parent, padding=16)
		self.repository = repository
		self.on_new = on_new
		self.on_edit = on_edit
		self.workouts: dict[str, Workout] = {}
		self.status_value = tk.StringVar()
		self.exercise_name = tk.StringVar()
		self.body_part = tk.StringVar()
		self.weekday = tk.StringVar(value="Any day")
		self.start_date = tk.StringVar()
		self.end_date = tk.StringVar()
		self.sort_by = tk.StringVar(value="Date")
		self._build()
		self.refresh()

	def _build(self) -> None:
		"""Create the history controls and result areas."""
		self.columnconfigure(0, weight=1)
		self.rowconfigure(2, weight=1)
		title = ttk.Label(self, text="Workout history", style="Title.TLabel")
		title.grid(row=0, column=0, sticky="w", pady=(0, 12))

		filters = ttk.LabelFrame(self, text="Filters", padding=10)
		filters.grid(row=1, column=0, sticky="ew", pady=(0, 12))
		for column in (1, 3, 5, 7):
			filters.columnconfigure(column, weight=1)
		self._filter_entry(filters, "Exercise", self.exercise_name, 0, 0)
		self._filter_entry(filters, "Body part", self.body_part, 0, 2)
		ttk.Label(filters, text="Weekday").grid(row=0, column=4, sticky="w", padx=(12, 6))
		ttk.Combobox(filters, textvariable=self.weekday, values=("Any day", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"), state="readonly", width=12).grid(row=0, column=5, sticky="ew")
		self._filter_entry(filters, "Start", self.start_date, 1, 0)
		self._filter_entry(filters, "End", self.end_date, 1, 2)
		ttk.Label(filters, text="Sort").grid(row=1, column=4, sticky="w", padx=(12, 6))
		ttk.Combobox(filters, textvariable=self.sort_by, values=("Date", "Exercise", "Body part", "Weekday"), state="readonly", width=12).grid(row=1, column=5, sticky="ew")
		ttk.Button(filters, text="Apply", command=self.refresh).grid(row=1, column=6, padx=(12, 4))
		ttk.Button(filters, text="Clear", command=self.clear_filters).grid(row=1, column=7)

		content = ttk.Panedwindow(self, orient="vertical")
		content.grid(row=2, column=0, sticky="nsew")
		results = ttk.Frame(content)
		results.columnconfigure(0, weight=1)
		results.rowconfigure(0, weight=1)
		self.tree = ttk.Treeview(results, columns=("date", "exercises", "notes"), show="headings", selectmode="browse")
		for column, heading, width in (("date", "Date", 110), ("exercises", "Exercises", 420), ("notes", "Notes", 300)):
			self.tree.heading(column, text=heading)
			self.tree.column(column, width=width, anchor="w")
		self.tree.grid(row=0, column=0, sticky="nsew")
		scrollbar = ttk.Scrollbar(results, orient="vertical", command=self.tree.yview)
		scrollbar.grid(row=0, column=1, sticky="ns")
		self.tree.configure(yscrollcommand=scrollbar.set)
		self.tree.bind("<<TreeviewSelect>>", self._show_selected)
		content.add(results, weight=3)

		self.detail = ttk.LabelFrame(content, text="Workout details", padding=10)
		self.detail.columnconfigure(0, weight=1)
		self.detail.rowconfigure(0, weight=1)
		self.detail_text = tk.Text(self.detail, height=9, state="disabled", wrap="word")
		self.detail_text.grid(row=0, column=0, sticky="nsew")
		content.add(self.detail, weight=2)

		actions = ttk.Frame(self)
		actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
		ttk.Label(actions, textvariable=self.status_value).pack(side="left")
		ttk.Button(actions, text="New workout", command=self._new_workout).pack(side="right")
		ttk.Button(actions, text="Edit selected", command=self._edit_selected).pack(side="right", padx=(0, 8))

	def _filter_entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, column: int) -> None:
		"""Add one labeled filter input to the filter grid."""
		tk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=(0, 6), pady=3)
		tk.Entry(parent, textvariable=variable).grid(row=row, column=column + 1, sticky="ew", pady=3)

	def clear_filters(self) -> None:
		"""Reset all filters and reload the complete history."""
		self.exercise_name.set("")
		self.body_part.set("")
		self.weekday.set("Any day")
		self.start_date.set("")
		self.end_date.set("")
		self.sort_by.set("Date")
		self.refresh()

	def refresh(self) -> None:
		"""Load filtered workouts into the result table."""
		try:
			start = date.fromisoformat(self.start_date.get().strip()) if self.start_date.get().strip() else None
			end = date.fromisoformat(self.end_date.get().strip()) if self.end_date.get().strip() else None
			weekday = self._weekday_value()
			workouts = self.repository.list_workouts(
				exercise_name=self.exercise_name.get().strip() or None,
				body_part=self.body_part.get().strip() or None,
				weekday=weekday,
				start_date=start,
				end_date=end,
				sort_by={"Date": "date", "Exercise": "exercise_name", "Body part": "body_part", "Weekday": "weekday"}[self.sort_by.get()],
			)
		except (KeyError, ValueError) as error:
			self.status_value.set(str(error))
			return
		self.workouts = {str(workout.id): workout for workout in workouts}
		for item in self.tree.get_children():
			self.tree.delete(item)
		for workout in workouts:
			exercises = self.repository.list_exercises(workout.id)
			summary = ", ".join(exercise.name for exercise in exercises) or "No exercises"
			self.tree.insert("", "end", iid=str(workout.id), values=(workout.workout_date.isoformat(), summary, workout.notes or ""))
		self.status_value.set(f"{len(workouts)} workout(s)")
		self._clear_detail()

	def _weekday_value(self) -> int | None:
		"""Convert the displayed weekday into SQLite's Sunday-first number."""
		if self.weekday.get() == "Any day":
			return None
		return ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday").index(self.weekday.get())

	def _selected_id(self) -> int | None:
		"""Return the selected workout ID, if any."""
		selection = self.tree.selection()
		return int(selection[0]) if selection else None

	def _show_selected(self, _event=None) -> None:
		"""Render the selected workout's exercises and sets."""
		workout_id = self._selected_id()
		if workout_id is None:
			self._clear_detail()
			return
		lines = []
		workout = self.workouts[str(workout_id)]
		if workout.notes:
			lines.append(f"Workout notes: {workout.notes}")
		for exercise in self.repository.list_exercises(workout_id):
			label = exercise.name
			if exercise.body_part:
				label += f" ({exercise.body_part})"
			lines.append(label)
			for exercise_set in self.repository.list_sets(exercise.id):
				weight = "" if exercise_set.weight is None else f" at {exercise_set.weight:g}"
				lines.append(f"  Set {exercise_set.set_number}: {exercise_set.reps} reps{weight}")
		self.detail_text.configure(state="normal")
		self.detail_text.delete("1.0", "end")
		self.detail_text.insert("1.0", "\n".join(lines) or "No workout details")
		self.detail_text.configure(state="disabled")

	def _clear_detail(self) -> None:
		"""Clear the detail panel when no workout is selected."""
		self.detail_text.configure(state="normal")
		self.detail_text.delete("1.0", "end")
		self.detail_text.configure(state="disabled")

	def _new_workout(self) -> None:
		"""Ask the shell to open a blank workout editor."""
		if self.on_new:
			self.on_new()

	def _edit_selected(self) -> None:
		"""Ask the shell to edit the selected workout."""
		workout_id = self._selected_id()
		if workout_id is not None and self.on_edit:
			self.on_edit(workout_id)
