# Planner Agent

Loads calendar, tasks and memory. Python computes actual free windows within the stored sample day's 5 PM–10:30 PM horizon. OpenAI selects unfinished task IDs in priority order and creates request-specific focus items with durations. Unknown/completed task IDs and invalid durations fail validation.

Python allocates the selected items, enforces calendar conflicts and ten-minute buffers, and writes `planner_output`. OpenAI summarizes the validated result. Evening review uses the next sample day. Calendar writes remain proposals requiring approval against the local SQLite calendar.
