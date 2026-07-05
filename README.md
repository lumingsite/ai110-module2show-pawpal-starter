# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

- **Priority-based scheduling** — packs today's plan high→medium→low priority within the owner's available minutes (`Scheduler.sort_by_priority()`, `generate_schedule()`).
- **Sorting by time** — view all pending tasks in chronological order, unscheduled tasks sorted last (`Scheduler.sort_by_time()`).
- **Conflict warnings** — flags overlapping fixed-time tasks, even across different pets (`Scheduler.detect_conflicts()`).
- **Daily/weekly recurrence** — completing a recurring task auto-spawns its next occurrence with the due date advanced (`Task.next_occurrence()`, `Pet.complete_task()`); one-off tasks don't respawn.
- **Filtering** — narrow tasks by pet and/or completion status, independently or combined (`Scheduler.filter_tasks()`).
- **Skip explanations** — tasks that don't fit today are skipped with a specific reason ("exceeds total available time" vs. "not enough remaining time") instead of silently dropped.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Daily plan for Alex:
  00:00 — [Biscuit] Morning Walk (30 min) [priority: high]
  00:30 — [Biscuit] Feeding (10 min) [priority: high]
  00:40 — [Mochi] Playtime (15 min) [priority: medium]

Skipped tasks:
  - [Mochi] Vet Checkup: exceeds total available time
  - [Biscuit] Grooming: not enough remaining time

--- After completing Morning Walk ---
Daily plan for Alex:
  00:00 — [Biscuit] Feeding (10 min) [priority: high]
  00:10 — [Mochi] Playtime (15 min) [priority: medium]
  00:25 — [Biscuit] Grooming (20 min) [priority: low]

Skipped tasks:
  - [Mochi] Vet Checkup: exceeds total available time
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
python -m pytest --cov
```

Tests live in `tests/test_pawpal.py` and cover core scheduling behaviors — sorting (chronological time order, unscheduled tasks last), recurrence (completing a daily/weekly task spawns the next occurrence), and conflict detection (overlapping fixed-time tasks across pets) — plus basic `Task`/`Pet` state changes:

| Test | What it verifies |
|------|-------------------|
| `test_mark_complete_changes_status` | `Task.mark_complete()` flips `is_completed`. |
| `test_add_task_increases_count` | `Pet.add_task()` appends to `Pet.tasks`. |
| `test_sort_by_time_returns_chronological_order` | `Scheduler.sort_by_time()` orders tasks by `"HH:MM"` string, with unscheduled tasks (`time=""`) sorted last. |
| `test_complete_daily_task_creates_next_day_task` | `Pet.complete_task()` marks a `"daily"` task done and auto-spawns its next occurrence one day later, incomplete. |
| `test_detect_conflicts_flags_duplicate_times` | `Scheduler.detect_conflicts()` flags overlapping fixed-time tasks across *different* pets (one owner, one clock). |

Sample test output (`python -m pytest`):

```
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/yingfei/codepath/ai 110/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 5 items

tests/test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.04s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | `sort_by_priority()` orders pending tasks high→low. `sort_by_time()` orders by the optional `Task.time` ("HH:MM"); unscheduled tasks sort last. O(n log n), string-key sort — no datetime parsing needed since times are zero-padded. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Filters the full task set (pending + completed) by optional pet name and/or completion status, combinable (e.g. "Mochi's pending tasks"). `Owner.get_all_tasks(include_completed=False)` backs it. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags overlapping fixed-time tasks (across pets too — one owner, one clock). Lightweight interval-overlap sweep: sort by start time, track the latest-ending task seen so far, flag any task starting before it ends. O(n log n), never crashes — returns a list of warning strings (empty if none). |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task(task_name)` | Completing a `"daily"`/`"weekly"` task auto-spawns its next occurrence (`due_date` advanced via `timedelta`) and appends it to the pet's task list; `"once"` tasks don't respawn. `Pet.complete_task()` is the entry point — it marks the task done and wires the spawn in one call. |

**Design note:** `Owner.pets` is a `dict[str, Pet]` keyed by name for O(1) add/remove/lookup. `Pet.tasks` stays a `list[Task]` on purpose — recurring tasks intentionally produce duplicate names (a completed task and its freshly spawned next occurrence share a name), so a dict keyed by name would silently drop one.

## 📸 Demo Walkthrough

### UI features

The Streamlit app (`app.py`) walks through three steps:

1. **Set Up Profile** — enter owner name, daily available minutes, and one pet's name/breed/age/special needs.
2. **Add Tasks** — for each task: name, category, duration, priority (high/medium/low), repeat frequency (once/daily/weekly), and an optional fixed time (`HH:MM`). Tasks appear in a running table; invalid input (bad time format, etc.) surfaces as an inline error.
3. **Generate Schedule** — builds today's plan and shows, in order: any conflict warnings, the sorted plan table, and any skipped tasks with reasons.

### Example workflow

1. Add owner "Alex" with 60 available minutes and pet "Biscuit."
2. Add tasks: "Morning Walk" (30 min, high, daily, 07:00), "Feeding" (10 min, high, daily, 12:00), "Grooming" (20 min, low, weekly, 18:00).
3. Click **Generate Schedule** — the app packs Morning Walk and Feeding into the 60-minute budget by priority, and skips Grooming with "not enough remaining time."
4. Add a "Brushing" task at 07:15 (overlaps Morning Walk's 07:00–07:30 slot) and regenerate — a conflict warning appears naming both tasks and their times.
5. Mark "Morning Walk" complete (via `Pet.complete_task()` in the backend) — a new "Morning Walk" instance is auto-spawned due the next day, since it's a `daily` task.

### Key Scheduler behaviors shown

- **Sorting** — `sort_by_priority()` orders the plan high→medium→low; `sort_by_time()` orders any task list chronologically by `HH:MM`, unscheduled tasks last.
- **Conflict warnings** — `detect_conflicts()` catches the Morning Walk / Brushing overlap above, even though they belong to the same pet, and would also catch overlaps across two different pets (one owner can't be in two places at once).
- **Recurrence** — completing a `daily`/`weekly` task spawns its next occurrence automatically; `once` tasks (like a one-time vet visit) never respawn.
- **Skip reasons** — a task longer than the entire daily budget is skipped as "exceeds total available time"; a task that would fit some days but not after higher-priority tasks ate the budget is skipped as "not enough remaining time."

### Sample CLI output (`python main.py`)

`main.py` exercises the same backend logic outside Streamlit — two pets, priority scheduling, sorting, a deliberate time conflict, recurrence, and filtering:

```
Daily plan for Alex:
  00:00 — [Biscuit] Morning Walk (30 min) [priority: high]
  00:30 — [Biscuit] Feeding (10 min) [priority: high]
  00:40 — [Mochi] Playtime (15 min) [priority: medium]

Skipped tasks:
  - [Mochi] Vet Checkup: exceeds total available time
  - [Biscuit] Grooming: not enough remaining time

--- All pending tasks sorted by time ---
  07:00  [Biscuit] Morning Walk
  08:00  [Mochi] Playtime
  12:00  [Biscuit] Feeding
  14:30  [Mochi] Vet Checkup
  18:00  [Biscuit] Grooming

--- Conflict check ---
  ⚠ Conflict: [Biscuit] Morning Walk (07:00) overlaps [Biscuit] Brushing (07:15)

--- After completing Morning Walk ---
Daily plan for Alex:
  00:00 — [Biscuit] Feeding (10 min) [priority: high]
  00:10 — [Biscuit] Morning Walk (30 min) [priority: high]
  00:40 — [Mochi] Playtime (15 min) [priority: medium]

Skipped tasks:
  - [Mochi] Vet Checkup: exceeds total available time
  - [Biscuit] Grooming: not enough remaining time
  - [Biscuit] Brushing: not enough remaining time

Auto-spawned recurrence: Morning Walk due 2026-07-06 (frequency=daily)
Vet Checkup respawned? False  (expected: False, frequency='once')

--- Filter: only Biscuit's tasks ---
  [Biscuit] Grooming (done=False)
  [Biscuit] Morning Walk (done=True)
  [Biscuit] Feeding (done=False)
  [Biscuit] Brushing (done=False)
  [Biscuit] Morning Walk (done=False)

--- Filter: only completed tasks ---
  [Biscuit] Morning Walk
  [Mochi] Vet Checkup

--- Filter: Mochi's pending tasks ---
  [Mochi] Playtime
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
