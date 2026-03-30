from pawpal_system import Pet, Task


def make_task(**overrides):
    defaults = dict(title="Walk", duration=20, priority="medium", category="exercise")
    return Task(**{**defaults, **overrides})


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(make_task(title="Morning walk"))
    pet.add_task(make_task(title="Evening walk"))
    assert len(pet.tasks) == 2
