from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    title: str
    duration: int
    priority: str
    category: str
    completed: bool = False

    def is_high_priority(self) -> bool:
        pass

    def to_dict(self) -> dict[str, Any]:
        pass

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_time: int
    pet: Pet

    def set_available_time(self, minutes: int) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.schedule: list[Task] = []

    def generate_plan(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def total_duration(self) -> int:
        pass
