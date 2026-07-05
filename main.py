from pawpal_system import Owner, Pet, Task, Scheduler


# --- Setup ---
biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
biscuit.add_task(Task("Morning Walk", "walk", duration_min=30, priority="high", is_recurring=True))
biscuit.add_task(Task("Feeding", "feeding", duration_min=10, priority="high", frequency="daily"))
biscuit.add_task(Task("Grooming", "grooming", duration_min=20, priority="low", frequency="weekly"))

mochi = Pet(name="Mochi", breed="Tabby Cat", age=2)
mochi.add_task(Task("Playtime", "enrichment", duration_min=15, priority="medium", is_recurring=True))
mochi.add_task(Task("Vet Checkup", "health", duration_min=90, priority="high", frequency="once",
                     description="Annual checkup — takes 90 min total with travel"))

owner = Owner(name="Alex", available_minutes=60)
owner.add_pet(biscuit)
owner.add_pet(mochi)

# --- Schedule ---
scheduler = Scheduler(owner)
print(scheduler.explain())

# --- Edge case: mark a task complete, reset cache, reschedule ---
print("\n--- After completing Morning Walk ---")
biscuit.tasks[0].mark_complete()
scheduler.reset()
print(scheduler.explain())
