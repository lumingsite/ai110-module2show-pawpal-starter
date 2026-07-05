from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Walk", "walk", 30)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_count():
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feeding", "feeding", 10))
    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order():
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    pet.add_task(Task("Dinner", "feeding", 15, time="18:00"))
    pet.add_task(Task("Breakfast", "feeding", 15, time="08:00"))
    pet.add_task(Task("Nail trim", "grooming", 10))  # unscheduled, no time
    pet.add_task(Task("Walk", "walk", 30, time="12:30"))

    owner = Owner(name="Sam", available_minutes=999)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    ordered_names = [task.name for _, task in scheduler.sort_by_time()]
    # Unscheduled tasks (time="") sort last behind the "24:00" sentinel.
    assert ordered_names == ["Breakfast", "Walk", "Dinner", "Nail trim"]


def test_complete_daily_task_creates_next_day_task():
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task(
        "Feed", "feeding", 10, frequency="daily", due_date=date(2026, 7, 5)
    )
    pet.add_task(task)

    spawned = pet.complete_task("Feed")

    assert task.is_completed is True
    assert spawned is not None
    assert spawned.is_completed is False
    assert spawned.due_date == date(2026, 7, 6)
    assert spawned in pet.tasks
    assert len(pet.tasks) == 2


def test_detect_conflicts_flags_duplicate_times():
    pet_a = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    pet_a.add_task(Task("Walk", "walk", 30, time="09:00"))

    pet_b = Pet(name="Whiskers", breed="Tabby", age=2)
    pet_b.add_task(Task("Vet call", "health", 20, time="09:00"))

    owner = Owner(name="Sam", available_minutes=999)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]
    assert "Walk" in warnings[0]
    assert "Vet call" in warnings[0]
