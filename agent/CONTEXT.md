## Purpose
Main: Personal workout tracker to log workouts by date, exercise, sets, reps, and optional notes/body part/image attachments.
Secondary: Provide quick viewing of exercise progression over time and easy filtering by workout date, exercise name, and body part.

## Technology Stack
- Language: Swift
- UI: SwiftUI
- Persistence: Core Data
- Local file storage: app Documents directory for image files
- Charts: Apple Charts on iOS 16+
- Architecture: MVVM with modular folders and simple services
- Platform: iOS 16+
- Dependencies: minimal; avoid external libraries unless clearly required

## Architecture Decisions
- Local-first application.
- Single-user (personal use only).
- No authentication initially.
- Use Core Data as the source of truth for workouts, exercises, sets, and bodyweight entries.
- Save images as files on disk and store file metadata in Core Data.
- Keep the initial data model simple and easy to change instead of over-normalizing.
- Use MVVM and modular feature folders to keep code maintainable.
- Target iOS 16+ so Apple Charts can be used for future graphs without adding third-party packages.

## Data Model
Primary entities:
1. Workout
- id: UUID
- date: Date
- notes: optional String
- exercises: relationship to Exercise

2. Exercise
- id: UUID
- name: String
- bodyPart: optional String
- notes: optional String
- workout: relationship to Workout
- sets: relationship to ExerciseSet

3. ExerciseSet
- id: UUID
- index: Int16
- reps: optional Int16
- weight: optional Double
- notes: optional String
- exercise: relationship to Exercise

4. Bodyweight
- id: UUID
- date: Date
- weight: Double
- notes: optional String

5. ImageAttachment
- id: UUID
- filename: String
- mimeType: optional String
- notes: optional String
- relationship to a workout, exercise, or bodyweight entry when relevant

Design notes:
- A workout contains many exercises, and each exercise contains many sets.
- Bodyweight is stored separately from workouts so it can be queried independently.
- Body part remains a plain String initially to keep the first version simple and flexible.
- The first scope does not include advanced analytics or heatmaps.

## Current Features
Planned initial features:
- Add a workout manually with a default or custom date.
- Add exercises to a workout with sets and reps.
- Track optional notes and body part for exercises.
- Filter workout history by date, exercise name, body part, and day of week.
- View progression by exercise over time.
- Log bodyweight entries separately.
- Attach images to workouts or exercises when relevant.

## Known Issues
- None recorded yet.
- Advanced analytics are intentionally deferred.

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
- Prefer functional components.
- Avoid unnecessary dependencies.
- Prefer clear, maintainable SwiftUI and Core Data code.
- Keep features modular and easy to extend later.
- Add comments where reasonable to help readability.

## Future Ideas (DO NOT IMPLEMENT YET)
- Allow mid-set entry and set-count increments.
- Add graphical progression over weeks, months, or years for specific exercises.
- Add a workout-frequency heatmap.
- Add bodyweight trend visualization.
- Add progress-photo support for bodyweight or exercise milestones.

You are helping me build a personal application. Your role is to act as a pragmatic software engineer and development partner.

Before writing code, briefly summarize your understanding and implementation plan.

Log (approved) decisions in DECISION_LOG.md with date "decision" and "reason".

## Current Task
Implement the approved first milestone only:
- define the Core Data model and local persistence structure,
- build the basic workout entry flow,
- enable workout history sorting/filtering,
- prepare the foundation for exercise progression and bodyweight tracking.

## Acceptance Criteria
- The app architecture matches the approved SwiftUI + Core Data plan.
- The data model supports workouts, exercises, sets, bodyweight, and optional image references.
- Invalid values cannot be submitted.
- Successful submission of data persists.
