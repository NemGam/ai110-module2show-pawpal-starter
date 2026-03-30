# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- Priority-based planning: `generate_plan()` sorts incomplete tasks by priority (`high` -> `medium` -> `low`) and then by pet name.
- Sorting by time: `build_time_schedule()` orders tasks chronologically (overdue first), using `due_at` when present and falling back to `HH:MM`.
- Auto planning window selection: `recommend_planning_window()` chooses `weekly` vs `monthly` based on upcoming due-date spread.
- Window-aware scheduling: time schedules include only tasks within the selected horizon (`7` days for weekly, `30` days for monthly).
- Conflict warnings: `detect_time_conflicts()` flags tasks that share the same scheduled start timestamp.
- Daily/weekly recurrence rollover: completing `daily` or `weekly` tasks creates the next occurrence instead of marking the old one complete.
- Completion workflow for one-time tasks: non-recurring tasks are marked complete and excluded from future schedules.
- Schedule filtering: supports filtering scheduled tasks by completion status and/or pet name.
- Total workload summary: `total_duration()` reports total planned minutes for the active schedule.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

The tests cover:

- Priority-based scheduling order
- Chronological sorting for time-based schedules
- Recurring task rollover for `daily` and `weekly` tasks
- Time conflict detection for duplicate task times

Confidence Level (based on latest test run): `4/5 stars`
