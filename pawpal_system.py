from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class TaskType(Enum):
    FEEDING = "feeding"
    WALKING = "walking"
    MEDICATION = "medication"
    GROOMING = "grooming"
    VET_APPOINTMENT = "vet_appointment"
    PLAYTIME = "playtime"
    TRAINING = "training"


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    type: TaskType
    due_at: datetime
    status: TaskStatus = TaskStatus.PENDING
    recurrence_days: int = 0
    priority: int = 1

    def mark_complete(self) -> None:
        raise NotImplementedError

    def reschedule(self, new_due_at: datetime) -> None:
        raise NotImplementedError

    def is_overdue(self, now: datetime) -> bool:
        raise NotImplementedError

    def create_next_recurring_task(self) -> Optional["Task"]:
        raise NotImplementedError


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    medical_notes: str
    owner_id: str
    tasks: list[Task] = field(default_factory=list)

    def update_weight(self, new_weight: float) -> None:
        raise NotImplementedError

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_upcoming_tasks(self) -> list[Task]:
        raise NotImplementedError


class Owner:
    def __init__(
        self,
        owner_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        address: str,
    ) -> None:
        self.owner_id = owner_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet_id: str) -> None:
        raise NotImplementedError

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        raise NotImplementedError

    def update_contact_info(self, email: str, phone: str, address: str) -> None:
        raise NotImplementedError


class Scheduler:
    def __init__(self, scheduler_id: str) -> None:
        self.scheduler_id = scheduler_id
        self.task_queue: list[Task] = []

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        raise NotImplementedError

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        raise NotImplementedError

    def send_reminders(self) -> None:
        raise NotImplementedError

    def complete_task(self, task_id: str) -> None:
        raise NotImplementedError
