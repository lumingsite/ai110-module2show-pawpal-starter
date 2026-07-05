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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
