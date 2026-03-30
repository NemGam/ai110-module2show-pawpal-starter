from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet-care activity with a duration, priority, and completion state."""

    title: str
    duration: int
    priority: str
    category: str
    time: str = "00:00"
    due_at: str = ""
    frequency: str = "once"
    completed: bool = False
    _next_occurrence_created: bool = field(default=False, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Normalize recurrence frequency and default unsupported values to one-time."""
        self.frequency = self.frequency.lower()
        if self.frequency not in {"once", "daily", "weekly"}:
            self.frequency = "once"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_recurring(self) -> bool:
        """Return True when this task should roll over after completion."""
        return self.frequency.lower() in {"daily", "weekly"}

    def create_next_occurrence(self) -> Task:
        """Create the next incomplete instance of this task."""
        next_due_at = self.due_at
        if self.due_at:
            parsed_due = self.parse_due_at()
            if parsed_due is not None:
                delta_days = 1 if self.frequency == "daily" else 7
                next_due_at = (parsed_due + timedelta(days=delta_days)).strftime("%Y-%m-%d %H:%M")

        return Task(
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            category=self.category,
            time=self.time,
            due_at=next_due_at,
            frequency=self.frequency,
            completed=False,
        )

    def parse_due_at(self) -> datetime | None:
        """Parse `due_at` value in YYYY-MM-DD HH:MM format."""
        if not self.due_at:
            return None
        try:
            return datetime.strptime(self.due_at, "%Y-%m-%d %H:%M")
        except ValueError:
            return None

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is 'high'."""
        return self.priority.lower() == "high"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the task to a plain dictionary."""
        return {
            "title": self.title,
            "duration": self.duration,
            "priority": self.priority,
            "category": self.category,
            "time": self.time,
            "due_at": self.due_at,
            "frequency": self.frequency,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Create a Task instance from a dictionary, defaulting completed to False."""
        return cls(
            title=data["title"],
            duration=data["duration"],
            priority=data["priority"],
            category=data["category"],
            time=data.get("time", "00:00"),
            due_at=data.get("due_at", ""),
            frequency=data.get("frequency", "once"),
            completed=data.get("completed", False),
        )


@dataclass
class Pet:
    """A pet with a name, species, and an associated list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the task matching the given title from the task list."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return all tasks sorted from highest to lowest priority."""
        return sorted(
            self.tasks,
            key=lambda t: PRIORITY_ORDER.get(t.priority.lower(), 99),
        )


@dataclass
class Owner:
    """A pet owner and a collection of pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all owned pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds prioritized care plans for the owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize a scheduler for a specific owner and an empty working schedule."""
        self.owner = owner
        self.schedule: list[tuple[Pet, Task]] = []

    def generate_plan(self) -> list[Task]:
        """Select and sort all incomplete tasks by priority and pet name."""
        all_pairs = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.tasks
            if not task.completed
        ]
        if not all_pairs:
            self.schedule = []
            return []
        all_pairs.sort(
            key=lambda pt: (
                PRIORITY_ORDER.get(pt[1].priority.lower(), 99),
                pt[0].name,
            )
        )
        self.schedule = all_pairs
        return [task for _, task in self.schedule]

    def recommend_planning_window(self, start: datetime | None = None) -> str:
        """Recommend a planning window based on how far upcoming due dates are spread."""
        anchor = start or datetime.now()
        due_dates = []
        for _, task in self.owner.all_tasks():
            due_dt = task.parse_due_at()
            if due_dt is not None and not task.completed and due_dt >= anchor:
                due_dates.append(due_dt)

        if not due_dates:
            return "weekly"

        farthest_due = max(due_dates)
        span_days = (farthest_due.date() - anchor.date()).days
        return "monthly" if span_days > 14 else "weekly"

    def build_time_schedule(self, window: str = "auto", start: datetime | None = None) -> list[tuple[Pet, Task]]:
        """Build a date/time-based schedule across a weekly or monthly planning window."""
        anchor = start or datetime.now()
        chosen_window = self.recommend_planning_window(anchor) if window == "auto" else window
        horizon_days = 30 if chosen_window == "monthly" else 7
        end = anchor + timedelta(days=horizon_days)

        pairs = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.tasks
            if not task.completed
        ]

        def sort_key(pair: tuple[Pet, Task]) -> tuple[int, datetime, int]:
            _, task = pair
            due_dt = task.parse_due_at()
            if due_dt is None:
                try:
                    hh, mm = task.time.split(":")
                    due_dt = anchor.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
                except (ValueError, TypeError):
                    due_dt = anchor

            overdue_rank = 0 if due_dt < anchor else 1
            priority_rank = PRIORITY_ORDER.get(task.priority.lower(), 99)
            return (overdue_rank, due_dt, priority_rank)

        pairs.sort(key=sort_key)

        selected: list[tuple[Pet, Task]] = []
        for pet, task in pairs:
            due_dt = task.parse_due_at()
            if due_dt is None:
                try:
                    hh, mm = task.time.split(":")
                    due_dt = anchor.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
                except (ValueError, TypeError):
                    due_dt = anchor

            if due_dt > end:
                continue

            selected.append((pet, task))

        self.schedule = selected
        return selected

    def mark_task_complete(self, pet_name: str, task_title: str, task_index: int = 0) -> Task:
        """Mark one task complete and roll recurring tasks forward in place."""
        pet = next((pet for pet in self.owner.pets if pet.name == pet_name), None)
        if pet is None:
            raise ValueError(f"Unknown pet: {pet_name}")

        matching_indices = [idx for idx, task in enumerate(pet.tasks) if task.title == task_title]
        if task_index < 0 or task_index >= len(matching_indices):
            raise IndexError("Task index out of range for the selected pet and title")

        absolute_idx = matching_indices[task_index]
        task = pet.tasks[absolute_idx]
        if task.completed:
            return task

        if task.is_recurring():
            pet.tasks[absolute_idx] = task.create_next_occurrence()
            return pet.tasks[absolute_idx]

        task.mark_complete()
        return task

    def detect_time_conflicts(self) -> list[str]:
        """Return warning messages for overlapping scheduled task start times."""
        if not self.schedule:
            return []

        conflicts_by_time: dict[str, list[str]] = {}
        for pet, task in self.schedule:
            due_dt = task.parse_due_at()
            time_key = due_dt.strftime("%Y-%m-%d %H:%M") if due_dt is not None else task.time
            label = f"{pet.name}: {task.title}"
            conflicts_by_time.setdefault(time_key, []).append(label)

        warnings: list[str] = []
        for time_key in sorted(conflicts_by_time):
            task_labels = conflicts_by_time[time_key]
            if len(task_labels) > 1:
                warnings.append(
                    f"WARNING: Time conflict at {time_key} -> " + ", ".join(task_labels)
                )
        return warnings

    def explain_plan(self) -> str:
        """Return scheduled tasks with cumulative offsets and requested HH:MM times."""
        if not self.schedule:
            return "No tasks scheduled."

        lines = [f"Plan for {self.owner.name}:"]
        elapsed = 0
        for pet, task in self.schedule:
            lines.append(
                f"  +{elapsed:>3} min  {task.time}  {pet.name}: [{task.priority.upper()}] {task.title}"
                f" - {task.duration} min ({task.category})"
            )
            elapsed += task.duration

        warnings = self.detect_time_conflicts()
        if warnings:
            lines.append("\nConflict warnings:")
            lines.extend(warnings)

        lines.append(f"\nTotal time planned: {self.total_duration()} min")
        return "\n".join(lines)

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return scheduled tasks filtered by completion status and/or pet name."""
        return [
            task
            for pet, task in self.schedule
            if (completed is None or task.completed == completed)
            and (pet_name is None or pet.name == pet_name)
        ]

    def sort_by_time(self) -> list[Task]:
        """Return scheduled tasks sorted by their time attribute in HH:MM format."""
        sorted_pairs = sorted(
            self.schedule,
            key=lambda pt: (int(pt[1].time.split(":")[0]), int(pt[1].time.split(":")[1])),
        )
        return [task for _, task in sorted_pairs]

    def total_duration(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(task.duration for _, task in self.schedule)
