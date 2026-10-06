# Planner Agent

Planner converts calendar events, tasks, memory preferences, and earlier agent outputs into a deterministic schedule proposal.

`tools.py` loads calendar events, tasks, and memory through the service layer. `agent.py` computes free time with timezone-aware datetimes, reserves blocks, inserts ten-minute buffers, and writes `planner_output`. Its demo planning horizon is the sample day's 5:00 PM–10:30 PM window.

The exact behavior depends on the selected workflow:

- `workout`: calculate availability for Fitness to consume.
- `study`: reserve concept, application, and practice blocks.
- `interview`: use Email's extracted interview details and reserve preparation time.
- `daily_plan` and `morning_digest`: allocate high-priority unfinished tasks.
- `afternoon_checkin`: reconsider the next unfinished tasks.
- `evening_review`: count completed work and identify tomorrow's first priority.

Planner writes available and planned blocks but never changes the calendar. During response building, planned blocks become `calendar.create` proposals. Only the approval endpoint can execute them against the local demo calendar, with a fresh conflict check.

When connecting Google Calendar and Tasks, keep recurrence handling, all-day event normalization, OAuth, and provider IDs in the service layer. Planner should continue receiving the same normalized structures.

