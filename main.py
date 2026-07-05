from pawpal_system import Owner, Pet, Task, Scheduler


# --- Setup (tasks added out of chronological order on purpose) ---
biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
biscuit.add_task(Task("Grooming", "grooming", duration_min=20, priority="low", frequency="weekly", time="18:00"))
biscuit.add_task(Task("Morning Walk", "walk", duration_min=30, priority="high", is_recurring=True, time="07:00"))
biscuit.add_task(Task("Feeding", "feeding", duration_min=10, priority="high", frequency="daily", time="12:00"))

mochi = Pet(name="Mochi", breed="Tabby Cat", age=2)
mochi.add_task(Task("Vet Checkup", "health", duration_min=90, priority="high", frequency="once", time="14:30",
                     description="Annual checkup — takes 90 min total with travel"))
mochi.add_task(Task("Playtime", "enrichment", duration_min=15, priority="medium", is_recurring=True, time="08:00"))

owner = Owner(name="Alex", available_minutes=60)
owner.add_pet(biscuit)
owner.add_pet(mochi)

# --- Schedule ---
scheduler = Scheduler(owner)
print(scheduler.explain())

# --- Sorting logic: sort_by_time() ---
print("\n--- All pending tasks sorted by time ---")
for pet, task in scheduler.sort_by_time():
    print(f"  {task.time or '--:--'}  [{pet.name}] {task.name}")

# --- Conflict detection: add a task that overlaps Morning Walk (07:00-07:30) on purpose ---
biscuit.add_task(Task("Brushing", "grooming", duration_min=10, priority="low", time="07:15"))
print("\n--- Conflict check ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠ {warning}")
else:
    print("  No conflicts detected.")

# --- Edge case: mark a task complete, reset cache, reschedule ---
print("\n--- After completing Morning Walk ---")
next_walk = biscuit.complete_task("Morning Walk")
scheduler.reset()
print(scheduler.explain())

if next_walk:
    print(f"\nAuto-spawned recurrence: {next_walk.name} due {next_walk.due_date} (frequency={next_walk.frequency})")

# --- Recurrence: complete the one-off Vet Checkup — should NOT respawn ---
respawn = mochi.complete_task("Vet Checkup")
print(f"Vet Checkup respawned? {respawn is not None}  (expected: False, frequency='once')")

# --- Filtering logic: filter_tasks() ---
print("\n--- Filter: only Biscuit's tasks ---")
for pet, task in scheduler.filter_tasks(pet_name="Biscuit"):
    print(f"  [{pet.name}] {task.name} (done={task.is_completed})")

print("\n--- Filter: only completed tasks ---")
for pet, task in scheduler.filter_tasks(completed=True):
    print(f"  [{pet.name}] {task.name}")

print("\n--- Filter: Mochi's pending tasks ---")
for pet, task in scheduler.filter_tasks(pet_name="Mochi", completed=False):
    print(f"  [{pet.name}] {task.name}")
