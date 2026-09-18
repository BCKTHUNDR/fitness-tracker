Proposal: Personal Fitness Tracker

## Technology Stack
- Python 3.10+
- Tkinter/ttk for the Windows desktop interface
- SQLite via the standard-library `sqlite3` module
- `pathlib` and `shutil` for local image files
- No external dependencies in the first milestone

The application will use a small layered structure: UI screens call application services, services validate input and coordinate operations, and repositories own SQLite queries. This keeps future web or Pythonista clients from depending on Tkinter details.

## Folder Structure

```text
src/fitness_tracker/
	__init__.py
	app.py
	config.py
	models.py
	database.py
	repositories/
		__init__.py
		workout_repository.py
		bodyweight_repository.py
	services/
		__init__.py
		workout_service.py
		bodyweight_service.py
	storage/
		__init__.py
		attachments.py
	ui/
		__init__.py
		main_window.py
		workout_entry.py
		workout_history.py
		bodyweight_entry.py
		exercise_history.py
tests/
	test_workouts.py
	test_bodyweight.py
```

The implementation should add modules only as the related feature is built.

## Data Model

### `workouts`
- `id`: unique identifier
- `workout_date`: editable date, defaulting to today
- `notes`: optional workout notes
- `created_at`: creation timestamp

### `exercises`
- `id`: unique identifier
- `workout_id`: parent workout
- `name`: exercise name
- `body_part`: optional body-part text
- `notes`: optional exercise notes
- `position`: order within the workout

An exercise row represents an occurrence in a specific workout. This preserves historical data when the same exercise is performed on multiple dates.

### `exercise_sets`
- `id`: unique identifier
- `exercise_id`: parent exercise occurrence
- `set_number`: ordered set number
- `reps`: required positive integer
- `weight`: optional numeric load
- `notes`: optional set notes

Sets are stored individually so the entry flow can support adding a set mid-workout and changing the new set's reps or weight.

### `bodyweight_entries`
- `id`: unique identifier
- `entry_date`: editable date
- `weight`: required numeric measurement
- `notes`: optional notes

Bodyweight is an independent entity and has no relationship to workouts.

### `image_attachments`
- `id`: unique identifier
- `workout_id`: optional parent workout
- `exercise_id`: optional parent exercise occurrence
- `bodyweight_id`: optional parent bodyweight entry
- `file_name`: local stored filename
- `original_name`: original filename for display
- `mime_type`: optional metadata
- `created_at`: creation timestamp

Image files are copied into local application storage. SQLite stores only metadata and references. A first-milestone attachment must belong to a workout, exercise, or bodyweight entry.

## Main Screens

1. **Workout Entry**
   - Date defaults to today and can be changed.
   - Add exercises, body parts, notes, and image attachments.
   - Add and order sets individually.
   - Increment set number and edit reps or weight.

2. **Bodyweight Entry**
   - Add a dated bodyweight measurement.
   - Add optional notes and image attachments.
   - Keep entries independent from workouts.

3. **Workout History**
   - Browse saved workouts.
   - Sort by date, weekday, exercise name, or body part.
   - Filter by date, weekday, exercise name, and body part.
   - Open a workout to inspect its exercises and sets.

4. **Exercise History**
   - Select an exercise and view prior sets grouped by workout date.
   - Filter by date range and body part.
   - Show tabular progression data; charts are deferred.

## Development Roadmap

1. Update project documentation and record the approved architecture and bodyweight decision.
2. Implement SQLite initialization, schema creation, and persistence helpers.
3. Implement workout, exercise, set, bodyweight, and attachment repositories.
4. Build validated workout and bodyweight entry flows.
5. Build history sorting, filtering, and detail views.
6. Build exercise history lookup.
7. Add focused tests for validation, persistence, ordering, sorting, and filtering.
8. Document local execution and testing.

Deferred: graphical progression charts, frequency heatmaps, export/import, authentication, cloud storage, and mobile-specific UI.