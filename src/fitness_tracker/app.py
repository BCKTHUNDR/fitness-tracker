"""Application composition root for the Tkinter desktop client."""

from __future__ import annotations

import tkinter as tk

from fitness_tracker.config import database_path
from fitness_tracker.database import Database
from fitness_tracker.services.workout_service import WorkoutService
from fitness_tracker.ui.main_window import MainWindow


def create_application(root: tk.Tk | None = None) -> tuple[tk.Tk, MainWindow]:
	"""Create an initialized database, shell window, and main view."""
	root = root or tk.Tk()
	root.title("Fitness tracker")
	root.geometry("1100x760")
	database = Database(database_path())
	database.initialize()
	window = MainWindow(root, WorkoutService(database))
	return root, window


def run() -> None:
	"""Start the desktop application's Tkinter event loop."""
	root, _window = create_application()
	root.mainloop()


