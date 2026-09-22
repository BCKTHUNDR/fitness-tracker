"""Minimal Tkinter form for creating and editing workouts."""

from __future__ import annotations

import tkinter as tk
from datetime import date, datetime
from tkinter import ttk

from fitness_tracker.services.inputs import ExerciseInput, SetInput, WorkoutDraft
from fitness_tracker.services.workout_service import WorkoutService

COLORS = {
	"background": "#1e1e1e",
	"surface": "#252526",
	"input": "#3c3c3c",
	"border": "#454545",
	"text": "#d4d4d4",
	"muted": "#9da1a6",
	"accent": "#569cd6",
	"danger": "#f48771",
}


class SetEditor(ttk.Frame):
	"""Edit one set while retaining its optional database ID."""

	def __init__(self, parent: tk.Misc, set_input: SetInput | None = None, on_remove=None) -> None:
		"""Create a compact set row with reps, weight, notes, and remove controls."""
		super().__init__(parent, style="Card.TFrame")
		set_input = set_input or SetInput(reps=1)
		self.set_id = set_input.id
		self.reps = tk.StringVar(value=str(set_input.reps))
		self.weight = tk.StringVar(value="" if set_input.weight is None else str(set_input.weight))
		self.notes = tk.StringVar(value=set_input.notes or "")
		ttk.Label(self, text="#", style="Muted.TLabel", width=3).grid(row=0, column=0, padx=(0, 6))
		self.number_label = ttk.Label(self, text="1", style="Muted.TLabel", width=3)
		self.number_label.grid(row=0, column=1, padx=(0, 8))
		self._entry("Reps", self.reps, 2, 7)
		self._entry("Weight", self.weight, 4, 7)
		self._entry("Notes", self.notes, 6, 24)
		self.remove_button = ttk.Button(self, text="Remove", command=on_remove, style="Subtle.TButton")
		self.remove_button.grid(row=0, column=8, padx=(8, 0))

	def _entry(self, label: str, variable: tk.StringVar, column: int, width: int) -> None:
		"""Add a labeled input to the set row."""
		ttk.Label(self, text=label, style="Muted.TLabel").grid(row=0, column=column, padx=(0, 4))
		ttk.Entry(self, textvariable=variable, width=width).grid(row=0, column=column + 1, padx=(0, 8))

	def set_number(self, number: int) -> None:
		"""Refresh the displayed one-based set number."""
		self.number_label.configure(text=str(number))

	def to_input(self) -> SetInput:
		"""Convert the row values into a set draft input."""
		weight = self.weight.get().strip()
		return SetInput(
			reps=int(self.reps.get().strip()),
			weight=float(weight) if weight else None,
			notes=self.notes.get().strip() or None,
			id=self.set_id,
		)


class ExerciseEditor(ttk.Frame):
	"""Edit one exercise and its dynamically managed set rows."""

	def __init__(self, parent: tk.Misc, exercise_input: ExerciseInput | None = None, on_remove=None) -> None:
		"""Create an exercise panel with fields and an add-set action."""
		super().__init__(parent, style="Card.TFrame", padding=10)
		exercise_input = exercise_input or ExerciseInput(name="")
		self.exercise_id = exercise_input.id
		self.name = tk.StringVar(value=exercise_input.name)
		self.body_part = tk.StringVar(value=exercise_input.body_part or "")
		self.notes = tk.StringVar(value=exercise_input.notes or "")
		self.set_rows: list[SetEditor] = []
		self.columnconfigure(1, weight=1)
		ttk.Label(self, text="Exercise", style="Muted.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 6))
		tk.Entry(self, textvariable=self.name, width=28).grid(row=0, column=1, sticky="ew")
		ttk.Label(self, text="Body part", style="Muted.TLabel").grid(row=0, column=2, padx=(12, 6))
		tk.Entry(self, textvariable=self.body_part, width=16).grid(row=0, column=3)
		ttk.Label(self, text="Notes", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0))
		tk.Entry(self, textvariable=self.notes).grid(row=1, column=1, columnspan=3, sticky="ew", pady=(8, 0))
		self.set_container = ttk.Frame(self, style="Card.TFrame")
		self.set_container.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(12, 4))
		self.set_container.columnconfigure(7, weight=1)
		for set_input in exercise_input.sets:
			self.add_set(set_input)
		if not self.set_rows:
			self.add_set()
		button_row = ttk.Frame(self, style="Card.TFrame")
		button_row.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))
		ttk.Button(button_row, text="Add set", command=self.add_set, style="Subtle.TButton").pack(side="left")
		ttk.Button(button_row, text="Remove exercise", command=on_remove, style="Danger.TButton").pack(side="left", padx=(8, 0))

	def add_set(self, set_input: SetInput | None = None) -> None:
		"""Append a set row and refresh set numbering."""
		row = SetEditor(self.set_container, set_input, on_remove=lambda: self.remove_set(row))
		row.pack(fill="x", pady=2)
		self.set_rows.append(row)
		self._renumber_sets()

	def remove_set(self, row: SetEditor) -> None:
		"""Remove a set row while keeping at least one set visible."""
		if len(self.set_rows) == 1:
			return
		row.destroy()
		self.set_rows.remove(row)
		self._renumber_sets()

	def _renumber_sets(self) -> None:
		"""Refresh all displayed set numbers after row changes."""
		for number, row in enumerate(self.set_rows, start=1):
			row.set_number(number)

	def to_input(self) -> ExerciseInput:
		"""Convert the exercise panel into an exercise draft input."""
		return ExerciseInput(
			name=self.name.get(),
			sets=tuple(row.to_input() for row in self.set_rows),
			body_part=self.body_part.get(),
			notes=self.notes.get(),
			id=self.exercise_id,
		)


class WorkoutEntryFrame(ttk.Frame):
	"""Provide a dark-friendly create/edit form for complete workouts."""

	def __init__(
		self,
		parent: tk.Misc,
		service: WorkoutService,
		workout_id: int | None = None,
		on_saved=None,
		on_cancel=None,
	) -> None:
		"""Build the workout form and optionally load an existing workout."""
		super().__init__(parent, style="App.TFrame", padding=16)
		self.service = service
		self.on_saved = on_saved
		self.on_cancel = on_cancel
		self.exercise_editors: list[ExerciseEditor] = []
		self.workout_id = workout_id
		self.date_value = tk.StringVar(value=datetime.now().astimezone().date().isoformat())
		self.notes_value = tk.StringVar()
		self.status_value = tk.StringVar()
		self._configure_styles()
		self._build_header()
		self._build_exercise_area()
		self._build_actions()
		if workout_id is not None:
			self._load_existing(workout_id)

	def _configure_styles(self) -> None:
		"""Configure restrained VS Code-like dark widget styles."""
		style = ttk.Style(self)
		style.configure("App.TFrame", background=COLORS["background"])
		style.configure("Card.TFrame", background=COLORS["surface"])
		style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
		style.configure("Muted.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
		style.configure("Title.TLabel", background=COLORS["background"], foreground=COLORS["text"], font=("Segoe UI", 16, "bold"))
		style.configure("TEntry", fieldbackground=COLORS["input"], foreground=COLORS["text"], insertcolor=COLORS["text"])
		style.configure("TButton", background=COLORS["surface"], foreground=COLORS["text"])
		style.configure("Accent.TButton", background=COLORS["accent"], foreground="#ffffff")
		style.configure("Subtle.TButton", background=COLORS["surface"], foreground=COLORS["text"])
		style.configure("Danger.TButton", background=COLORS["surface"], foreground=COLORS["danger"])
		style.configure("Error.TLabel", background=COLORS["background"], foreground=COLORS["danger"])

	def _build_header(self) -> None:
		"""Build the date and workout notes controls."""
		self.columnconfigure(1, weight=1)
		ttk.Label(self, text="Edit workout" if self.workout_id else "New workout", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
		ttk.Label(self, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=(18, 0))
		ttk.Entry(self, textvariable=self.date_value, width=14).grid(row=1, column=1, sticky="w", pady=(18, 0))
		tk.Label(self, text="Workout notes").grid(row=2, column=0, sticky="w", pady=(8, 0))
		tk.Entry(self, textvariable=self.notes_value).grid(row=2, column=1, sticky="ew", pady=(8, 0))

	def _build_exercise_area(self) -> None:
		"""Build the scrollable exercise list and add-exercise action."""
		self.exercise_container = ttk.Frame(self, style="App.TFrame")
		self.exercise_container.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(18, 0))
		self.rowconfigure(3, weight=1)
		self.exercise_container.columnconfigure(0, weight=1)
		ttk.Button(self.exercise_container, text="Add exercise", command=self.add_exercise, style="Subtle.TButton").grid(row=0, column=0, sticky="w", pady=(0, 8))
		self.exercise_list = ttk.Frame(self.exercise_container, style="App.TFrame")
		self.exercise_list.grid(row=1, column=0, sticky="nsew")
		self.exercise_container.rowconfigure(1, weight=1)

	def _build_actions(self) -> None:
		"""Build status, cancel, and save controls."""
		self.status_label = ttk.Label(self, textvariable=self.status_value, style="Error.TLabel")
		self.status_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 4))
		actions = ttk.Frame(self, style="App.TFrame")
		actions.grid(row=5, column=0, columnspan=2, sticky="e")
		ttk.Button(actions, text="Cancel", command=self.cancel, style="Subtle.TButton").pack(side="left", padx=(0, 8))
		ttk.Button(actions, text="Save workout", command=self.save, style="Accent.TButton").pack(side="left")

	def _load_existing(self, workout_id: int) -> None:
		"""Populate the form from an existing workout draft."""
		try:
			draft = self.service.load_workout_for_edit(workout_id)
		except ValueError as error:
			self.status_value.set(str(error))
			return
		self.date_value.set(
			draft.workout_date.isoformat()
			if draft.workout_date
			else datetime.now().astimezone().date().isoformat()
		)
		self.notes_value.set(draft.notes or "")
		for exercise in draft.exercises:
			self.add_exercise(exercise)

	def add_exercise(self, exercise_input: ExerciseInput | None = None) -> None:
		"""Append an exercise editor to the form."""
		row = ExerciseEditor(self.exercise_list, exercise_input, on_remove=lambda: self.remove_exercise(row))
		row.pack(fill="x", pady=(0, 8))
		self.exercise_editors.append(row)

	def remove_exercise(self, row: ExerciseEditor) -> None:
		"""Remove an exercise editor from the unsaved draft."""
		row.destroy()
		self.exercise_editors.remove(row)

	def to_draft(self) -> WorkoutDraft:
		"""Convert current widget values into an immutable workout draft."""
		parsed_date = date.fromisoformat(self.date_value.get().strip())
		return WorkoutDraft(
			workout_date=parsed_date,
			exercises=tuple(editor.to_input() for editor in self.exercise_editors),
			notes=self.notes_value.get(),
			id=self.workout_id,
		)

	def save(self) -> None:
		"""Validate widgets through the service and notify the parent on success."""
		try:
			saved = self.service.save_workout(self.to_draft())
		except (TypeError, ValueError) as error:
			self.status_value.set(str(error))
			return
		self.status_value.set("Saved")
		if self.on_saved:
			self.on_saved(saved)

	def cancel(self) -> None:
		"""Notify the parent that the form should be closed without saving."""
		if self.on_cancel:
			self.on_cancel()
