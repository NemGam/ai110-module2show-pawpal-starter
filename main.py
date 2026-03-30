from pawpal_system import Owner, Pet, Task, Scheduler

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog")
whiskers = Pet(name="Whiskers", species="Cat")

# --- Tasks for Buddy ---
buddy.add_task(Task(title="Morning walk",       duration=30, priority="high",   category="exercise"))
buddy.add_task(Task(title="Flea treatment",     duration=10, priority="high",   category="health"))
buddy.add_task(Task(title="Play fetch",         duration=20, priority="medium", category="exercise"))

# --- Tasks for Whiskers ---
whiskers.add_task(Task(title="Brush fur",       duration=15, priority="medium", category="grooming"))
whiskers.add_task(Task(title="Clean litter box",duration=10, priority="high",   category="hygiene"))
whiskers.add_task(Task(title="Laser pointer play", duration=10, priority="low", category="exercise"))

# --- Owner ---
alex = Owner(name="Alex", available_time=70)
alex.add_pet(buddy)
alex.add_pet(whiskers)

# --- Scheduler ---
scheduler = Scheduler(owner=alex)
scheduler.generate_plan()

print("=" * 40)
print("       PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 40)
print(scheduler.explain_plan())
print("=" * 40)
