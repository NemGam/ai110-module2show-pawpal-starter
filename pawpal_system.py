from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet-care activity with a duration, priority, and completion state."""

    title: str
    duration: int
    priority: str
    category: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
    """A pet owner with a daily time budget and a collection of pets."""

    name: str
    available_time: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        """Update the owner's available time in minutes."""
        self.available_time = minutes

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all owned pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a prioritized daily care plan within the owner's available time."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.schedule: list[tuple[Pet, Task]] = []

    def generate_plan(self) -> list[Task]:
        """Fill the schedule greedily with incomplete tasks in priority order."""
        all_pairs = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.get_tasks_by_priority()
            if not task.completed
        ]
        self.schedule = []
        time_remaining = self.owner.available_time
        for pet, task in all_pairs:
            if task.duration <= time_remaining:
                self.schedule.append((pet, task))
                time_remaining -= task.duration
        return [task for _, task in self.schedule]

    def explain_plan(self) -> str:
        """Return a formatted string of the scheduled tasks grouped by pet."""
        if not self.schedule:
            return "No tasks scheduled."
        lines = [f"Plan for {self.owner.name} ({self.owner.available_time} min available):"]
        by_pet: dict[str, list[Task]] = {}
        for pet, task in self.schedule:
            by_pet.setdefault(pet.name, []).append(task)
        for pet_name, tasks in by_pet.items():
            lines.append(f"\n  {pet_name}:")
            for task in tasks:
                lines.append(
                    f"    [{task.priority.upper()}] {task.title} — {task.duration} min ({task.category})"
                )
        lines.append(f"\nTotal time used: {self.total_duration()} / {self.owner.available_time} min")
        return "\n".join(lines)

    def total_duration(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(task.duration for _, task in self.schedule)
