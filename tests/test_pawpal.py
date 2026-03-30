from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime


def make_task(**overrides):
    defaults = dict(title="Walk", duration=20, priority="medium", category="exercise")
    return Task(**{**defaults, **overrides})


def make_scheduler(tasks):
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="dog")
    for task in tasks:
        pet.add_task(task)
    owner.add_pet(pet)
    return Scheduler(owner=owner)


# --- Existing tests ---

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


# --- Scheduler: priority ordering ---

def test_high_priority_scheduled_before_low():
    scheduler = make_scheduler([
        make_task(title="Low task", duration=20, priority="low"),
        make_task(title="High task", duration=20, priority="high"),
    ])
    scheduled = scheduler.generate_plan()
    titles = [t.title for t in scheduled]
    assert titles.index("High task") < titles.index("Low task")


def test_priority_order_high_medium_low():
    scheduler = make_scheduler([
        make_task(title="Low", duration=20, priority="low"),
        make_task(title="Medium", duration=20, priority="medium"),
        make_task(title="High", duration=20, priority="high"),
    ])
    scheduled = scheduler.generate_plan()
    titles = [t.title for t in scheduled]
    assert titles == ["High", "Medium", "Low"]


# --- Scheduler: time budget ---

def test_long_task_is_not_skipped_without_budget_limit():
    scheduler = make_scheduler([
        make_task(title="Long", duration=60, priority="high"),
        make_task(title="Short", duration=20, priority="low"),
    ])
    scheduled = scheduler.generate_plan()
    titles = [t.title for t in scheduled]
    assert "Long" in titles
    assert "Short" in titles


def test_total_duration_includes_all_incomplete_tasks():
    scheduler = make_scheduler([
        make_task(title="A", duration=30, priority="high"),
        make_task(title="B", duration=30, priority="medium"),
        make_task(title="C", duration=20, priority="low"),
    ])
    scheduler.generate_plan()
    assert scheduler.total_duration() == 80


def test_all_tasks_included_when_they_fit():
    scheduler = make_scheduler([
        make_task(title="A", duration=20, priority="high"),
        make_task(title="B", duration=30, priority="medium"),
        make_task(title="C", duration=10, priority="low"),
    ])
    scheduled = scheduler.generate_plan()
    assert len(scheduled) == 3


# --- Scheduler: completed tasks ---

def test_completed_tasks_excluded():
    scheduler = make_scheduler([
        make_task(title="Done", duration=20, priority="high", completed=True),
        make_task(title="Pending", duration=20, priority="low"),
    ])
    scheduled = scheduler.generate_plan()
    titles = [t.title for t in scheduled]
    assert "Done" not in titles
    assert "Pending" in titles


# --- Scheduler: recurring rollover ---

def test_daily_completion_creates_next_incomplete_instance():
    scheduler = make_scheduler([
        make_task(title="Feed", duration=10, priority="high", frequency="daily"),
    ])

    scheduler.mark_task_complete("Buddy", "Feed")

    tasks = scheduler.owner.pets[0].tasks
    assert len(tasks) == 1
    assert tasks[0].completed is False
    assert tasks[0].frequency == "daily"


def test_weekly_completion_creates_next_incomplete_instance():
    scheduler = make_scheduler([
        make_task(title="Groom", duration=20, priority="medium", frequency="weekly"),
    ])

    scheduler.mark_task_complete("Buddy", "Groom")

    tasks = scheduler.owner.pets[0].tasks
    assert len(tasks) == 1
    assert tasks[0].completed is False
    assert tasks[0].frequency == "weekly"


def test_once_completion_does_not_create_new_instance():
    scheduler = make_scheduler([
        make_task(title="Checkup", duration=30, priority="high", frequency="once"),
    ])

    scheduler.mark_task_complete("Buddy", "Checkup")

    tasks = scheduler.owner.pets[0].tasks
    assert len(tasks) == 1
    assert tasks[0].completed is True


def test_repeated_completion_does_not_duplicate_recurring_instance():
    scheduler = make_scheduler([
        make_task(title="Walk", duration=20, priority="high", frequency="daily"),
    ])

    scheduler.mark_task_complete("Buddy", "Walk")
    scheduler.mark_task_complete("Buddy", "Walk")

    tasks = scheduler.owner.pets[0].tasks
    assert len(tasks) == 1
    assert tasks[0].title == "Walk"
    assert tasks[0].completed is False


def test_daily_completion_rolls_due_at_forward_one_day():
    scheduler = make_scheduler([
        make_task(
            title="Feed",
            duration=10,
            priority="high",
            frequency="daily",
            due_at="2026-03-30 08:00",
        ),
    ])

    scheduler.mark_task_complete("Buddy", "Feed")

    tasks = scheduler.owner.pets[0].tasks
    assert len(tasks) == 1
    assert tasks[0].due_at == "2026-03-31 08:00"


# --- Scheduler: time-based planning window ---

def test_recommend_planning_window_weekly_for_near_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(make_task(due_at="2026-03-31 08:00"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    recommended = scheduler.recommend_planning_window(start=datetime(2026, 3, 30, 9, 0))
    assert recommended == "weekly"


def test_recommend_planning_window_monthly_for_far_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(make_task(due_at="2026-04-25 08:00"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    recommended = scheduler.recommend_planning_window(start=datetime(2026, 3, 30, 9, 0))
    assert recommended == "monthly"


def test_build_time_schedule_includes_multiple_same_day_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(make_task(title="A", duration=20, priority="high", due_at="2026-03-30 08:00"))
    pet.add_task(make_task(title="B", duration=20, priority="medium", due_at="2026-03-30 09:00"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    selected_pairs = scheduler.build_time_schedule(window="weekly", start=datetime(2026, 3, 30, 7, 0))
    selected_titles = [task.title for _, task in selected_pairs]
    assert selected_titles == ["A", "B"]


# --- Scheduler: multi-pet global priority ---

def test_multi_pet_high_priority_beats_other_pet_low():
    owner = Owner(name="Alex")
    pet1 = Pet(name="Buddy", species="dog")
    pet2 = Pet(name="Whiskers", species="cat")
    pet1.add_task(make_task(title="Dog low", duration=20, priority="low"))
    pet2.add_task(make_task(title="Cat high", duration=20, priority="high"))
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner=owner)
    scheduled = scheduler.generate_plan()
    titles = [t.title for t in scheduled]
    assert titles.index("Cat high") < titles.index("Dog low")


# --- explain_plan ---

def test_explain_plan_contains_owner_name():
    scheduler = make_scheduler([make_task(title="Walk", duration=20, priority="high")])
    scheduler.generate_plan()
    assert "Alex" in scheduler.explain_plan()


def test_explain_plan_empty_schedule():
    scheduler = make_scheduler([])
    scheduler.generate_plan()
    assert scheduler.explain_plan() == "No tasks scheduled."


def test_explain_plan_shows_start_offsets():
    scheduler = make_scheduler([
        make_task(title="First", duration=15, priority="high"),
        make_task(title="Second", duration=10, priority="low"),
    ])
    scheduler.generate_plan()
    plan = scheduler.explain_plan()
    assert "+  0 min" in plan
    assert "+ 15 min" in plan


def test_explain_plan_includes_task_time():
    scheduler = make_scheduler([
        make_task(title="Breakfast", duration=15, priority="high", time="08:15"),
    ])
    scheduler.generate_plan()
    plan = scheduler.explain_plan()
    assert "08:15" in plan


def test_detect_time_conflicts_for_same_pet_tasks():
    scheduler = make_scheduler([
        make_task(title="Morning walk", time="08:00"),
        make_task(title="Breakfast", time="08:00"),
    ])
    scheduler.generate_plan()

    warnings = scheduler.detect_time_conflicts()
    assert len(warnings) == 1
    assert "WARNING: Time conflict at 08:00" in warnings[0]
    assert "Buddy: Morning walk" in warnings[0]
    assert "Buddy: Breakfast" in warnings[0]


def test_detect_time_conflicts_for_different_pets():
    owner = Owner(name="Alex")
    dog = Pet(name="Buddy", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    dog.add_task(make_task(title="Walk", time="09:00"))
    cat.add_task(make_task(title="Litter", time="09:00"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()

    warnings = scheduler.detect_time_conflicts()
    assert len(warnings) == 1
    assert "WARNING: Time conflict at 09:00" in warnings[0]
    assert "Buddy: Walk" in warnings[0]
    assert "Whiskers: Litter" in warnings[0]


def test_explain_plan_includes_conflict_warning():
    scheduler = make_scheduler([
        make_task(title="Task A", time="10:30"),
        make_task(title="Task B", time="10:30"),
    ])
    scheduler.generate_plan()
    plan = scheduler.explain_plan()

    assert "Conflict warnings:" in plan
    assert "WARNING: Time conflict at 10:30" in plan
