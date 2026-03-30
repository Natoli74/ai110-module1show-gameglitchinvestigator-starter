from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents one care activity for a pet."""

    description: str
    time: str
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """Mark task complete and create next occurrence for recurring tasks."""
        self.completed = True

        normalized = self.frequency.strip().lower()
        if normalized == "daily":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        if normalized == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=7),
            )
        return None

    def scheduled_at(self) -> datetime:
        """Return datetime used for chronological sorting."""
        hour, minute = map(int, self.time.split(":"))
        return datetime.combine(self.due_date, datetime.min.time()).replace(
            hour=hour,
            minute=minute,
        )


@dataclass
class Pet:
    """Stores pet profile and associated care tasks."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return number of tasks currently assigned."""
        return len(self.tasks)


@dataclass
class Owner:
    """Manages a collection of pets for one owner."""

    name: str
    pets: dict[str, Pet] = field(default_factory=dict)

    def add_pet(self, name: str, species: str, age: int) -> Pet:
        """Create and store a pet record, replacing any duplicate name."""
        pet = Pet(name=name, species=species, age=age)
        self.pets[name] = pet
        return pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return a pet by name if it exists."""
        return self.pets.get(name)

    def all_pets(self) -> list[Pet]:
        """Return all pets for this owner."""
        return list(self.pets.values())

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        payload = {
            "name": self.name,
            "pets": {
                pet_name: {
                    "name": pet.name,
                    "species": pet.species,
                    "age": pet.age,
                    "tasks": [
                        {
                            "description": task.description,
                            "time": task.time,
                            "frequency": task.frequency,
                            "due_date": task.due_date.isoformat(),
                            "completed": task.completed,
                        }
                        for task in pet.tasks
                    ],
                }
                for pet_name, pet in self.pets.items()
            },
        }

        with open(filepath, "w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load owner, pets, and tasks from a JSON file if present."""
        if not Path(filepath).exists():
            return cls(name="PawPal User")

        try:
            with open(filepath, "r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except (json.JSONDecodeError, OSError):
            return cls(name="PawPal User")

        owner = cls(name=payload.get("name", "PawPal User"))

        for pet_name, pet_payload in payload.get("pets", {}).items():
            pet = Pet(
                name=pet_payload.get("name", pet_name),
                species=pet_payload.get("species", "Unknown"),
                age=int(pet_payload.get("age", 0)),
            )

            for task_payload in pet_payload.get("tasks", []):
                due_date_str = task_payload.get("due_date", date.today().isoformat())
                try:
                    task_due_date = date.fromisoformat(due_date_str)
                except ValueError:
                    task_due_date = date.today()

                pet.add_task(
                    Task(
                        description=task_payload.get("description", "Task"),
                        time=task_payload.get("time", "09:00"),
                        frequency=task_payload.get("frequency", "once"),
                        due_date=task_due_date,
                        completed=bool(task_payload.get("completed", False)),
                    )
                )

            owner.pets[pet.name] = pet

        return owner


class Scheduler:
    """Coordinates schedule views and task operations across all pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize scheduler with an owner context."""
        self.owner = owner

    def get_all_tasks(self, include_completed: bool = True) -> list[tuple[str, Task]]:
        """Collect tasks from every pet."""
        rows: list[tuple[str, Task]] = []
        for pet in self.owner.all_pets():
            for task in pet.tasks:
                if include_completed or not task.completed:
                    rows.append((pet.name, task))
        return rows

    def sort_by_time(self, tasks: Optional[list[tuple[str, Task]]] = None) -> list[tuple[str, Task]]:
        """Sort task rows by due date then HH:MM time."""
        source = tasks if tasks is not None else self.get_all_tasks()
        return sorted(source, key=lambda row: row[1].scheduled_at())

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[tuple[str, Task]]:
        """Filter tasks by pet name and/or completion status."""
        rows = self.get_all_tasks(include_completed=True)
        if pet_name:
            rows = [row for row in rows if row[0] == pet_name]
        if completed is not None:
            rows = [row for row in rows if row[1].completed is completed]
        return rows

    def add_task_to_pet(self, pet_name: str, task: Task) -> bool:
        """Add a task to a pet by name and return success."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False
        pet.add_task(task)
        return True

    def mark_task_complete(self, pet_name: str, task_index: int) -> Optional[Task]:
        """Complete a pet task and append next recurring occurrence if needed."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return None
        if task_index < 0 or task_index >= len(pet.tasks):
            return None

        next_task = pet.tasks[task_index].mark_complete()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def detect_conflicts(self) -> list[str]:
        """Return warnings when two tasks share the same date/time."""
        warnings: list[str] = []
        slots: dict[tuple[date, str], list[str]] = {}

        for pet_name, task in self.get_all_tasks(include_completed=False):
            key = (task.due_date, task.time)
            slots.setdefault(key, []).append(f"{pet_name}: {task.description}")

        for (due_date, at_time), entries in slots.items():
            if len(entries) > 1:
                details = "; ".join(entries)
                warnings.append(
                    f"Conflict at {due_date.isoformat()} {at_time}: {details}"
                )

        return warnings

    def todays_schedule(self) -> list[tuple[str, Task]]:
        """Return non-completed tasks due today in chronological order."""
        today = date.today()
        rows = [
            row
            for row in self.get_all_tasks(include_completed=False)
            if row[1].due_date == today
        ]
        return self.sort_by_time(rows)
