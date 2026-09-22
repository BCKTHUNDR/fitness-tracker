"""Main Tkinter application window and view navigation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from fitness_tracker.repositories.workout_repository import WorkoutRepository
from fitness_tracker.services.workout_service import WorkoutService
from fitness_tracker.ui.workout_entry import WorkoutEntryFrame
from fitness_tracker.ui.workout_history import WorkoutHistoryFrame


class MainWindow(ttk.Frame):
	"""Own the application shell and coordinate the primary workout views."""

	def __init__(self, root: tk.Tk, service: WorkoutService) -> None:
		"""Create navigation and the initial workout history view."""
		super().__init__(root)
		self.root = root
		self.service = service
		self.repository = WorkoutRepository(service.database)
		self.current_view: ttk.Frame | None = None
		self.pack(fill="both", expand=True)
		self._configure_styles()
		self._build_shell()
		self.show_history()

	def _configure_styles(self) -> None:
		"""Configure the shared dark application palette."""
		style = ttk.Style(self)
		style.configure("App.TFrame", background="#1e1e1e")
		style.configure("Title.TLabel", background="#1e1e1e", foreground="#d4d4d4", font=("Segoe UI", 16, "bold"))
		style.configure("TLabel", background="#1e1e1e", foreground="#d4d4d4")

	def _build_shell(self) -> None:
		"""Build the navigation rail and content container."""
		self.configure(style="App.TFrame")
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)
		navigation = ttk.Frame(self, padding=12, style="App.TFrame")
		navigation.grid(row=0, column=0, sticky="ns")
		ttk.Label(navigation, text="Fitness tracker", style="Title.TLabel").pack(anchor="w", pady=(0, 18))
		ttk.Button(navigation, text="Workout history", command=self.show_history).pack(fill="x", pady=2)
		ttk.Button(navigation, text="New workout", command=self.new_workout).pack(fill="x", pady=2)
		self.content = ttk.Frame(self, padding=0, style="App.TFrame")
		self.content.grid(row=0, column=1, sticky="nsew")
		self.content.columnconfigure(0, weight=1)
		self.content.rowconfigure(0, weight=1)

	def _show(self, view: ttk.Frame) -> None:
		"""Replace the active content view with a new frame."""
		if self.current_view is not None:
			self.current_view.destroy()
		self.current_view = view
		view.grid(row=0, column=0, sticky="nsew")

	def show_history(self) -> None:
		"""Show a freshly loaded workout history view."""
		self._show(WorkoutHistoryFrame(self.content, self.repository, on_new=self.new_workout, on_edit=self.edit_workout))

	def new_workout(self) -> None:
		"""Open the blank workout editor."""
		self._show(WorkoutEntryFrame(self.content, self.service, on_saved=self._workout_saved, on_cancel=self.show_history))

	def edit_workout(self, workout_id: int) -> None:
		"""Open the workout editor for an existing workout."""
		self._show(WorkoutEntryFrame(self.content, self.service, workout_id=workout_id, on_saved=self._workout_saved, on_cancel=self.show_history))

	def _workout_saved(self, _workout) -> None:
		"""Return to history after a successful workout save."""
		self.show_history()
