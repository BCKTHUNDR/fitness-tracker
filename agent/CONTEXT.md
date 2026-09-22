## Purpose
Main: Personal workout tracker for recording workouts by date, exercise, sets, reps, optional weight, notes, body part, and image attachments.
Secondary: Provide quick lookup of exercise history and progression data, with filtering by date, weekday, exercise name, and body part.

## Technology Stack
- Language: Python 3.10+
- Desktop UI: Tkinter and ttk from the Python standard library
- Persistence: SQLite through Python's built-in `sqlite3` module
- Attachment storage: local application data directory using `pathlib` and `shutil`
- Architecture: small layered modules separating data access, application logic, and UI
- Primary platform: Windows desktop
- Future platforms: a web UI or Pythonista/iOS client may reuse the domain and persistence boundaries
- Application dependencies: Python standard library only
- Development dependency: pytest through `uv run pytest`

## Architecture Decisions
- Local-first application for one user, with no authentication or cloud services.
- SQLite is the source of truth for structured records and is initialized through an explicit schema/migration path.
- Image files are copied into local application storage; SQLite stores attachment metadata and references.
- The UI must not contain database queries directly; repositories and services own persistence and validation.
- Keep body parts as plain text initially rather than introducing a separate lookup table.
- Keep the first implementation modular but small enough for a personal application.
- The desktop UI is the first client; future web or mobile support is not part of the first milestone.
- Use immutable input drafts for service boundaries; an ID-bearing `WorkoutDraft` supports both creation and editing.
- Save complete workout aggregates transactionally; cancellation before save makes no database changes.
- Preserve existing workout, exercise, and set IDs during edits so attachment relationships remain valid.
- Use a minimal Tkinter/ttk UI with a VS Code-like dark palette.

## Data Model
Primary entities:
1. Workout
- id: unique identifier
- workout_date: user-selected date, defaulting to today
- notes: optional workout-level notes
- created_at: record creation timestamp
- exercises: related exercise occurrences

2. Exercise occurrence
- id: unique identifier
- workout_id: parent workout
- name: exercise name
- body_part: optional plain-text body part
- notes: optional exercise notes
- position: order within the workout
- sets: related exercise sets

3. Exercise set
- id: unique identifier
- exercise_id: parent exercise occurrence
- set_number: set order, allowing mid-workout increments
- reps: positive integer repetitions
- weight: optional numeric load for progression lookup
- notes: optional set notes

4. Bodyweight entry
- id: unique identifier
- entry_date: user-selected date
- weight: required numeric measurement
- notes: optional notes
- image attachments: optional related attachments

Bodyweight is a separate entity and is not attached to workouts.

5. Image attachment
- id: unique identifier
- workout_id: optional parent workout
- exercise_id: optional parent exercise occurrence
- bodyweight_id: optional parent bodyweight entry
- file_name: local stored filename
- original_name: original filename for display
- mime_type: optional metadata
- created_at: attachment timestamp

Design notes:
- A workout contains many exercise occurrences; each occurrence contains ordered sets.
- The same exercise name can occur in multiple workouts without overwriting history.
- Bodyweight entries can be queried independently from workouts.
- Attachment binary data stays in the filesystem rather than in SQLite.
- Graphs and heatmaps are deferred; the first milestone provides structured data suitable for them later.
- `WorkoutDraft`, `ExerciseInput`, and `SetInput` may carry optional IDs. Missing IDs represent new records; omitted existing child IDs are removed during an edit.

## Current Features
Implemented:
- SQLite schema versioning, initialization, foreign-key enforcement, indexes, and attachment ownership constraints.
- Repository persistence for workouts, exercises, sets, bodyweight entries, and attachment metadata.
- Workout history filters for exercise name, body part, weekday, and inclusive start/end date windows.
- Workout creation service with validation, transactional persistence, and rollback/orphan cleanup.
- Bodyweight service with date defaults and positive finite-weight validation.
- ID-aware workout editing that updates retained rows, inserts new children, deletes omitted exercises/sets, and preserves attachments.
- Minimal dark-friendly Tkinter workout entry form for creating and editing workouts, including dynamic exercise and set rows.
- Focused automated tests for persistence, validation, ordering, filtering, editing, attachment preservation, and rollback.

Planned first-milestone follow-up:
- Integrate the workout entry form into the main application window.
- Build workout history and detail views.
- Add the bodyweight entry UI.
- Add attachment file-copy workflow and UI controls.
- Build exercise history and progression lookup.

## Known Issues
- None recorded yet.
- Graphical progression charts and workout-frequency heatmaps are intentionally deferred.

## Constraints
- Prioritize simplicity and maintainability.
- Avoid unnecessary dependencies.
- Do not over-engineer for large-scale usage.
- Preserve existing functionality when modifying the project.
- Prefer local-first solutions where practical.
- Ask questions when requirements are genuinely ambiguous.
- Do not introduce new dependencies unless necessary.
- Prefer existing components and utilities.
- Do not rewrite working code.
- Do not create placeholder functionality disguised as complete functionality.
- If an API or feature cannot be implemented fully, explain why.
- Do not assume requirements that have not been specified.
- Keep the first implementation focused on the approved scope.
- Must work offline.
- No paid APIs.
- No cloud database.
- Make one line summary within definition of functions and classes.

## Development Rules
1. Inspect existing code before making changes.
2. Propose a plan before implementing substantial features.
3. Implement one feature at a time.
4. Do not modify unrelated files.
5. Explain important architectural decisions.
6. After implementation, describe how to test the changes.
7. Do not automatically add features that were not requested.
8. Keep the app local-first and dependency-light.

## Coding Conventions
- Prefer standard-library solutions and clear Python types.
- Keep UI event handling separate from database access.
- Use parameterized SQL and explicit validation.
- Keep features modular and easy to extend later.
- Add comments only where the implementation is not self-explanatory.

## Future Ideas (DO NOT IMPLEMENT YET)
- Add graphical progression over weeks, months, or years for specific exercises.
- Add a workout-frequency heatmap.
- Add bodyweight trend visualization.
- Add export/import and backup workflows.
- Add a web or mobile client over the shared application/domain layer.
- Add an autosaved active-workout session for crash recovery and mid-workout entry.

You are helping me build a personal application. Your role is to act as a pragmatic software engineer and development partner.

Before writing code, briefly summarize your understanding and implementation plan.

Log (approved) decisions in DECISION_LOG.md with date "decision" and "reason".

Development Roadmap:
1 Update project documentation to the Python desktop-first direction. (complete)
2 Add the SQLite schema, initialization, and migration mechanism. (complete)
3 Implement workout, exercise, set, and attachment data access. (complete)
4 Build the workout entry workflow with validation and persistence. (partially complete: services and workout entry UI implemented; bodyweight UI and attachment workflow remain)
5 Build history sorting, filtering, and detail views. (next)
6 Build exercise history lookup.
7 Add focused tests for validation, persistence, sorting, filtering, set ordering, and editing. (mostly complete; expand with UI tests as UI grows)
8 Document how to run and test the application.
9 Defer graphical progression charts, workout heatmaps, export/import, autosaved active-workout recovery, and mobile-specific UI.


## Current Task
Continue the approved first milestone:
- integrate the workout entry UI into the application shell,
- build workout history and detail views,
- implement the bodyweight entry UI,
- implement attachment file storage and entry controls,
- build exercise history lookup and progression foundations.

## Acceptance Criteria
- The app architecture matches the approved Python desktop-first plan.
- The data model supports workouts, exercises, sets, bodyweight entries, and optional image references.
- Bodyweight entries are independent of workouts.
- Invalid values cannot be submitted.
- Successful submissions persist after reopening the application.
- Editing a saved workout preserves retained record IDs and attachment relationships.
- Failed create/edit saves leave no partial workout changes.
