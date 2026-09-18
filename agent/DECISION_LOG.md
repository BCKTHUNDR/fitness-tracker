2026-09-18 - decision: Use Python 3.10+, Tkinter/ttk, and SQLite for the first implementation, replacing the previous SwiftUI/Core Data direction.
reason: The target is now a Windows desktop application; standard-library components keep it offline, dependency-light, maintainable, and easier to adapt to a future web or Pythonista client.

2026-09-18 - decision: Include bodyweight tracking in the first milestone as a separate entity with its own date, measurement, notes, and optional image attachments.
reason: Bodyweight is approved for the initial scope, but it must remain independent from workouts so it can be recorded on days without a workout.

2026-09-18 - decision: Store image files locally and keep only attachment metadata and references in SQLite.
reason: This keeps the database small while supporting offline attachments for workouts, exercises, and bodyweight entries.

2026-09-18 - decision: Use a versioned SQLite schema with foreign-key enforcement, indexed lookup fields, and an attachment check requiring exactly one owner.
reason: These constraints protect historical data integrity and provide a simple migration path while supporting the planned workout, exercise, set, bodyweight, and attachment queries.

2026-09-18 - decision: Keep SQLite access behind dedicated workout, bodyweight, and attachment repositories, with allowlisted history sort fields.
reason: This preserves separation between UI and persistence, supports future clients, and prevents user-selected history sorting from becoming arbitrary SQL.
