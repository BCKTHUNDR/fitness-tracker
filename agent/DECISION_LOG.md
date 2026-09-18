2026-09-18 - decision: Use Python 3.10+, Tkinter/ttk, and SQLite for the first implementation, replacing the previous SwiftUI/Core Data direction.
reason: The target is now a Windows desktop application; standard-library components keep it offline, dependency-light, maintainable, and easier to adapt to a future web or Pythonista client.

2026-09-18 - decision: Include bodyweight tracking in the first milestone as a separate entity with its own date, measurement, notes, and optional image attachments.
reason: Bodyweight is approved for the initial scope, but it must remain independent from workouts so it can be recorded on days without a workout.

2026-09-18 - decision: Store image files locally and keep only attachment metadata and references in SQLite.
reason: This keeps the database small while supporting offline attachments for workouts, exercises, and bodyweight entries.
