I want to build a personal fitness tracker. 

Purpose:
Store information about past workouts (exercises, number of sets/reps, additional notes, image attachments)
Allow quick lookup of progression of each exercise over different timespans.
Allow quick lookup of data of exercises done for certain body parts. 
Graphical overview (e.g. weight) over time shows progression at a glance.

Users:
Single user (me).

Platform:
PC (windows)
Future support: Mobile (iOS, either through webapp or Pythonista)

Core functionality:
1. Store information about past workouts that are entered manually. The information should stay after reopening/resetting the app.
2. Allow user to input exercise name, number of sets, number of reps in each set. Optionally: body part, additional notes, image attachments. The input should default to being under the present date, but also allowed to designate an earlier date to store the exercise info in.
3. Lookup information about past workouts, sorted based on: day of the week, exercise name, body part, specific date.
4. Allow exercise info to be input mid set. I.e. Allow set number to be easily incremented, and modify the number of reps in the new set if desired by the user.

Nice to haves (DO NOT IMPLEMENT YET):
1. Graphical representation of progression over time of different exercises.
2. Heatmap of workout frequency over months.

Constraints:
- Prioritize simplicity and maintainability.
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
- Features implemented modularly (easy to maintain and modify later).

Before generating code, propose:
- Technology stack.
- Folder structure.
- Data model.
	- identify the main entities and propose a simple data model. Explain what each field represents and how the entities relate to each other. Do not implement anything yet.
- Main screens.
- Development roadmap.

Wait for my approval before implementation.
When making decisions, add it to DECISION_LOG.md noting the date along with "decision:" and "reason:"