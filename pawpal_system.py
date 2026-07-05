from dataclasses import dataclass, field, replace
from datetime import date, timedelta

_FREQUENCY_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _time_to_minutes(hhmm: str) -> int:
    hh, mm = hhmm.split(":")
    return int(hh) * 60 + int(mm)


@dataclass
class Task:
    name: str
    category: str
    duration_min: int
    description: str = ""
    priority: str = "medium"        # "high", "medium", "low"
    frequency: str = "daily"        # "daily", "weekly", "once"
    is_recurring: bool = False
    is_completed: bool = False
    time: str = ""                  # optional fixed time, "HH:MM" 24hr; "" = unscheduled
    due_date: date = field(default_factory=date.today)

    def __post_init__(self):
        if self.priority not in ("high", "medium", "low"):
            raise ValueError(f"priority must be 'high', 'medium', or 'low'")
        if self.frequency not in ("daily", "weekly", "once"):
            raise ValueError(f"frequency must be 'daily', 'weekly', or 'once'")
        if self.time:
            hh, _, mm = self.time.partition(":")
            if not (hh.isdigit() and mm.isdigit() and 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
                raise ValueError(f"time must be 'HH:MM' in 24hr format, got {self.time!r}")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def reset(self) -> None:
        """Reset this task to incomplete."""
        self.is_completed = False

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, incomplete copy due on the next occurrence, or None for one-off tasks.

        O(1): one dict lookup for the frequency step (daily=+1 day, weekly=+1
        week) plus dataclasses.replace() to clone every field except the two
        overridden (is_completed, due_date) — no manual field-by-field copy.
        """
        step = _FREQUENCY_STEP.get(self.frequency)
        if step is None:
            return None
        return replace(self, is_completed=False, due_date=self.due_date + step)


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.is_completed]

    def complete_task(self, task_name: str) -> Task | None:
        """Mark a task complete; if it recurs (daily/weekly), auto-add its next occurrence.

        O(n) linear scan over this pet's tasks to find the first name match
        (names aren't unique once recurrence spawns duplicates, so a dict
        keyed by name would silently collide — see Owner.pets for where the
        dict-by-name optimization *was* safe to apply).
        Returns the newly spawned Task, or None if the task doesn't recur / wasn't found.
        """
        for task in self.tasks:
            if task.name == task_name:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task
        return None


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: dict[str, Pet] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, keyed by name, to this owner (O(1))."""
        self.pets[pet.name] = pet

    def get_pet(self, pet_name: str) -> Pet | None:
        """Look up a pet by name (O(1))."""
        return self.pets.get(pet_name)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name (O(1))."""
        self.pets.pop(pet_name, None)

    def get_all_tasks(self, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs across all pets; pending only unless include_completed=True."""
        if include_completed:
            return [(pet, task) for pet in self.pets.values() for task in pet.tasks]
        return [(pet, task) for pet in self.pets.values() for task in pet.get_pending_tasks()]


class Scheduler:
    _PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}

    def __init__(self, owner: Owner):
        self.owner = owner
        self._schedule: list[dict] | None = None
        self._skipped: list[tuple[Pet, Task, str]] | None = None

    def sort_by_priority(self) -> list[tuple[Pet, Task]]:
        """Return all pending (pet, task) pairs sorted from highest to lowest priority."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda pt: self._PRIORITY_ORDER[pt[1].priority])

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all pending (pet, task) pairs sorted by scheduled time (HH:MM); unscheduled tasks sort last.

        O(n log n) via sorted()'s Timsort. The key is the raw "HH:MM" string —
        since it's always zero-padded, lexicographic order equals chronological
        order, so no int/datetime parsing is needed. Unscheduled tasks (time="")
        sort last behind the "24:00" sentinel.
        """
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda pt: pt[1].time or "24:00")

    def detect_conflicts(self) -> list[str]:
        """Return a warning string for each pair of fixed-time tasks whose intervals overlap.

        Lightweight interval-overlap sweep: sort by start time, track the
        latest-ending task seen so far, and flag any task that starts before
        it ends. O(n log n), no crash — just returns warnings (empty if none).
        Applies across pets too: one owner can't do two things at once.
        """
        timed = sorted(
            ((pet, task) for pet, task in self.owner.get_all_tasks() if task.time),
            key=lambda pt: _time_to_minutes(pt[1].time),
        )
        if not timed:
            return []

        warnings = []
        holder_pet, holder_task = timed[0]
        holder_end = _time_to_minutes(holder_task.time) + holder_task.duration_min
        for pet, task in timed[1:]:
            start = _time_to_minutes(task.time)
            if start < holder_end:
                warnings.append(
                    f"Conflict: [{holder_pet.name}] {holder_task.name} ({holder_task.time}) overlaps "
                    f"[{pet.name}] {task.name} ({task.time})"
                )
            end = start + task.duration_min
            if end > holder_end:
                holder_pet, holder_task, holder_end = pet, task, end
        return warnings

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs matching an optional pet name and/or completion status.

        O(n) single pass: both filters are optional predicates combined with
        AND, short-circuited via `is None` checks so an omitted filter costs
        nothing extra rather than requiring a separate pass per filter.
        """
        all_tasks = self.owner.get_all_tasks(include_completed=True)
        return [
            (pet, task) for pet, task in all_tasks
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.is_completed == completed)
        ]

    def filter_by_time(
        self, pet_tasks: list[tuple[Pet, Task]]
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task, str]]]:
        """Split tasks into scheduled and skipped based on available time."""
        scheduled, skipped = [], []
        remaining = self.owner.available_minutes
        for pet, task in pet_tasks:
            if task.duration_min > self.owner.available_minutes:
                skipped.append((pet, task, "exceeds total available time"))
            elif task.duration_min <= remaining:
                scheduled.append((pet, task))
                remaining -= task.duration_min
            else:
                skipped.append((pet, task, "not enough remaining time"))
        return scheduled, skipped

    def generate_schedule(self) -> list[dict]:
        """Build and cache the daily schedule; returns cached result on subsequent calls."""
        if self._schedule is not None:
            return self._schedule

        sorted_tasks = self.sort_by_priority()
        scheduled, skipped = self.filter_by_time(sorted_tasks)

        plan, current_min = [], 0
        for pet, task in scheduled:
            plan.append({
                "pet": pet,
                "task": task,
                "start_min": current_min,
                "end_min": current_min + task.duration_min,
            })
            current_min += task.duration_min

        self._schedule = plan
        self._skipped = skipped
        return self._schedule

    def explain(self) -> str:
        """Return a human-readable summary of the schedule and any skipped tasks."""
        schedule = self.generate_schedule()

        lines = [f"Daily plan for {self.owner.name}:"]
        for item in schedule:
            h, m = divmod(item["start_min"], 60)
            t = item["task"]
            lines.append(
                f"  {h:02d}:{m:02d} — [{item['pet'].name}] {t.name} ({t.duration_min} min) [priority: {t.priority}]"
            )

        if self._skipped:
            lines.append("\nSkipped tasks:")
            for pet, task, reason in self._skipped:
                lines.append(f"  - [{pet.name}] {task.name}: {reason}")

        return "\n".join(lines)

    def reset(self) -> None:
        """Clear cached schedule so generate_schedule() reruns on next call."""
        self._schedule = None
        self._skipped = None
