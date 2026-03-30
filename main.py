from pawpal_system import Owner, Pet, Task, Scheduler

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog")
whiskers = Pet(name="Whiskers", species="Cat")

# --- Tasks for Buddy (added out of order by time) ---
buddy.add_task(Task(title="Evening walk",      duration=30, priority="high",   category="exercise", time="18:00"))
buddy.add_task(Task(title="Morning walk",      duration=30, priority="high",   category="exercise", time="08:00"))
buddy.add_task(Task(title="Breakfast",         duration=15, priority="medium", category="feeding",  time="08:00"))
buddy.add_task(Task(title="Flea treatment",    duration=10, priority="high",   category="health",   time="09:00"))
buddy.add_task(Task(title="Play fetch",        duration=20, priority="medium", category="exercise", time="14:00"))

# --- Tasks for Whiskers (also out of order, includes overlap at 08:00) ---
whiskers.add_task(Task(title="Laser pointer play",  duration=10, priority="low",    category="exercise", time="20:00"))
whiskers.add_task(Task(title="Clean litter box",    duration=10, priority="high",   category="hygiene",  time="08:00"))
whiskers.add_task(Task(title="Brush fur",           duration=15, priority="medium", category="grooming", time="11:30"))

# Mark one task complete to demonstrate filtering
buddy.tasks[3].mark_complete()  # Flea treatment

# --- Owner ---
alex = Owner(name="Alex")
alex.add_pet(buddy)
alex.add_pet(whiskers)

# --- Scheduler ---
scheduler = Scheduler(owner=alex)
scheduler.generate_plan()

print("=" * 45)
print("        PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 45)
print(scheduler.explain_plan())

# --- explicit conflict check ---
print()
print("=" * 45)
print("            CONFLICT WARNINGS")
print("=" * 45)
conflicts = scheduler.detect_time_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No conflicts detected.")

# --- sort_by_time ---
print()
print("=" * 45)
print("         SORTED BY TIME (HH:MM)")
print("=" * 45)
for task in scheduler.sort_by_time():
    print(f"  {task.time}  [{task.priority.upper():6}] {task.title}")

# --- filter_tasks: incomplete only ---
print()
print("=" * 45)
print("         FILTER: INCOMPLETE TASKS")
print("=" * 45)
for task in scheduler.filter_tasks(completed=False):
    print(f"  [{task.priority.upper():6}] {task.title}")

# --- filter_tasks: by pet name ---
print()
print("=" * 45)
print("         FILTER: BUDDY'S TASKS")
print("=" * 45)
for task in scheduler.filter_tasks(pet_name="Buddy"):
    print(f"  [{task.priority.upper():6}] {task.title}")

# --- filter_tasks: incomplete + pet name combined ---
print()
print("=" * 45)
print("   FILTER: WHISKERS' INCOMPLETE TASKS")
print("=" * 45)
for task in scheduler.filter_tasks(completed=False, pet_name="Whiskers"):
    print(f"  [{task.priority.upper():6}] {task.title}")

print()
print("=" * 45)
