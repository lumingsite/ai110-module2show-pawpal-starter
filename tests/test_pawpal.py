from pawpal_system import Pet, Task


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
