Proposal: Personal Fitness Tracker

Data model (main entities)
1) Workout
- id (UUID): unique identifier
- date (Date): date/time of workout (default: now, editable)
- notes (String, optional): overall workout notes
- exercises (to-many relationship -> Exercise)

2) Exercise
- id (UUID)
- name (String): exercise name ("Bench Press")
- bodyPart (String, optional): e.g., "Chest", "Legs"
- notes (String, optional)
- sets (to-many relationship -> ExerciseSet)
- workout (inverse to-one relationship -> Workout)

3) ExerciseSet
- id (UUID)
- index (Int16): set number/order within exercise
- reps (Int16, optional): reps completed
- weight (Double, optional): weight used (if applicable)
- notes (String, optional)
- exercise (inverse relationship -> Exercise)

4) Bodyweight (separate entity for daily weight logs)
- id (UUID)
- date (Date)
- weight (Double)
- notes (String, optional)

5) ImageAttachment
- id (UUID)
- filename (String): filename within Documents
- mimeType (String, optional)
- notes (String, optional)
- (relationship optional) linkedToExercise | linkedToWorkout | linkedToBodyweight

Relationships and design notes
- A `Workout` contains many `Exercise` objects; each `Exercise` has ordered `ExerciseSet` children.
- Images are stored as files; Core Data stores lightweight metadata and file URL/filename to keep DB small.
- Keep types simple (Strings for `bodyPart`) to avoid over-normalization; later we can extract a BodyPart enum table if needed.
- Add lightweight indexing on `Exercise.name` and `Workout.date` for fast queries.

Main screens
- Dashboard: quick overview, recent workouts, quick-add shortcut, bodyweight sparkline
- Log Workout: form to add a past workout (default date = today) with multiple exercises and per-set inputs; image attachments and notes
- Working out: interface to add exercises to current workout, allowing set count to be incremented and reps adjusted; image attachments and notes
- Workout History: chronological list of workouts with filters (by date range, day-of-week)
- Exercise Library / Exercise Detail: list of exercises; tapping an exercise shows progression (list + small chart) and ability to filter by date ranges/body part
- Bodyweight: add/view measurements and a graph over time
- Settings / Export: backup/export local data (e.g., JSON) and import