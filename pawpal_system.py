from dataclasses import dataclass, field


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

    def __post_init__(self):
        if self.priority not in ("high", "medium", "low"):
            raise ValueError(f"priority must be 'high', 'medium', or 'low'")
        if self.frequency not in ("daily", "weekly", "once"):
            raise ValueError(f"frequency must be 'daily', 'weekly', or 'once'")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def reset(self) -> None:
        """Reset this task to incomplete."""
        self.is_completed = False


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


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name from this owner's pet list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs for every pending task across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_pending_tasks()]


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
