from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional


class TaskType(Enum):
    """Kinds of care activities for a pet."""

    FEEDING = "feeding"
    WALKING = "walking"
    MEDICATION = "medication"
    GROOMING = "grooming"
    VET_APPOINTMENT = "vet_appointment"
    PLAYTIME = "playtime"
    TRAINING = "training"


class TaskStatus(Enum):
    """Lifecycle state of a task."""

    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


@dataclass
class Task:
    """A single pet care activity with time, optional recurrence, and status."""

    task_id: str
    title: str
    description: str
    type: TaskType
    due_at: datetime
    pet_id: str
    status: TaskStatus = TaskStatus.PENDING
    recurrence_days: int = 0
    priority: int = 1

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = TaskStatus.COMPLETED

    def reschedule(self, new_due_at: datetime) -> None:
        """Move the due time to a new datetime."""
        self.due_at = new_due_at

    def is_overdue(self, now: datetime) -> bool:
        """Return True if still pending and the due time is before now."""
        if self.status != TaskStatus.PENDING:
            return False
        return self.due_at < now

    def create_next_recurring_task(self) -> Optional["Task"]:
        """If recurrence_days > 0, return a new pending task for the next occurrence."""
        if self.recurrence_days <= 0:
            return None
        next_due = self.due_at + timedelta(days=self.recurrence_days)
        return Task(
            task_id=f"{self.task_id}_next_{next_due.timestamp()}",
            title=self.title,
            description=self.description,
            type=self.type,
            due_at=next_due,
            pet_id=self.pet_id,
            status=TaskStatus.PENDING,
            recurrence_days=self.recurrence_days,
            priority=self.priority,
        )


@dataclass
class Pet:
    """Pet profile and tasks owned by this pet."""

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
        """Update the pet's weight in the same units as stored."""
        self.weight = new_weight

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, ensuring pet_id matches."""
        if task.pet_id != self.pet_id:
            task.pet_id = self.pet_id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by id from this pet's list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_upcoming_tasks(self) -> list[Task]:
        """Return pending tasks sorted soonest due first."""
        pending = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        return sorted(pending, key=lambda t: t.due_at)


class Owner:
    """An owner with contact info and a collection of pets."""

    def __init__(
        self,
        owner_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        address: str,
    ) -> None:
        """Create an owner with contact fields and an empty pet list."""
        self.owner_id = owner_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pet.owner_id = self.owner_id
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet by id from this owner."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        """Return the pet with the given id, or None."""
        for p in self.pets:
            if p.pet_id == pet_id:
                return p
        return None

    def update_contact_info(self, email: str, phone: str, address: str) -> None:
        """Replace email, phone, and address."""
        self.email = email
        self.phone = phone
        self.address = address

    def get_all_tasks(self) -> list[Task]:
        """Flatten all tasks from all pets for scheduling."""
        out: list[Task] = []
        for pet in self.pets:
            out.extend(pet.tasks)
        return out


class Scheduler:
    """Coordinates tasks across an owner's pets: query, order, and complete by id."""

    def __init__(self, scheduler_id: str, owner: Owner) -> None:
        """Attach this scheduler to an owner for cross-pet task queries."""
        self.scheduler_id = scheduler_id
        self.owner = owner
        self.task_queue: list[Task] = []

    def _refresh_queue(self) -> None:
        """Rebuild the in-memory queue from the owner's pets."""
        self.task_queue = list(self.owner.get_all_tasks())

    def add_task(self, task: Task) -> None:
        """Add a task to the correct pet and refresh the queue."""
        pet = self.owner.get_pet_by_id(task.pet_id)
        if pet is None:
            raise ValueError(f"No pet with id {task.pet_id!r} for this owner.")
        pet.add_task(task)
        self._refresh_queue()

    def remove_task(self, task_id: str) -> None:
        """Remove a task from whichever pet holds it."""
        for pet in self.owner.pets:
            before = len(pet.tasks)
            pet.remove_task(task_id)
            if len(pet.tasks) < before:
                break
        self._refresh_queue()

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Return all tasks for one pet."""
        pet = self.owner.get_pet_by_id(pet_id)
        if pet is None:
            return []
        return list(pet.tasks)

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        """Return tasks due on a calendar day, sorted by time then priority."""
        self._refresh_queue()
        day_tasks = [t for t in self.task_queue if t.due_at.date() == target_date]
        return sorted(day_tasks, key=lambda t: (t.due_at, -t.priority))

    def get_today_schedule(self, today: date | None = None) -> list[Task]:
        """Return today's tasks in schedule order (same rules as get_tasks_for_date)."""
        d = today if today is not None else date.today()
        return self.get_tasks_for_date(d)

    def send_reminders(self) -> None:
        """Placeholder: could notify for overdue or soon-due tasks; no-op for CLI."""
        return

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted by due datetime ascending (uses due_at, not string times)."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda t: t.due_at)

    def filter_by_status(
        self,
        status: TaskStatus,
        tasks: Optional[list[Task]] = None,
    ) -> list[Task]:
        """Return only tasks whose status matches (e.g. pending or completed)."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.status == status]

    def filter_by_pet_name(
        self,
        name_substring: str,
        tasks: Optional[list[Task]] = None,
        *,
        case_insensitive: bool = True,
    ) -> list[Task]:
        """Return tasks whose pet's name contains the given substring."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        needle = name_substring.strip()
        if not needle:
            return list(source)

        def name_for(task: Task) -> str:
            pet = self.owner.get_pet_by_id(task.pet_id)
            return pet.name if pet else ""

        if case_insensitive:
            lowered = needle.lower()
            return [t for t in source if lowered in name_for(t).lower()]
        return [t for t in source if needle in name_for(t)]

    def detect_time_conflicts(
        self,
        target_date: Optional[date] = None,
        *,
        tasks: Optional[list[Task]] = None,
    ) -> list[str]:
        """Return warning strings when two or more tasks share the same calendar day and clock minute."""
        self._refresh_queue()
        pool = list(tasks) if tasks is not None else list(self.task_queue)
        if target_date is not None:
            pool = [t for t in pool if t.due_at.date() == target_date]

        slots: dict[tuple[int, int, int, int, int], list[Task]] = defaultdict(list)
        for t in pool:
            dt = t.due_at
            key = (dt.year, dt.month, dt.day, dt.hour, dt.minute)
            slots[key].append(t)

        warnings: list[str] = []
        for (y, mo, d, h, mi), group in slots.items():
            if len(group) < 2:
                continue
            slot_label = datetime(y, mo, d, h, mi).strftime("%Y-%m-%d %H:%M")
            labels: list[str] = []
            for task in group:
                pet = self.owner.get_pet_by_id(task.pet_id)
                pet_label = pet.name if pet else task.pet_id
                labels.append(f"{pet_label}: {task.title}")
            warnings.append(f"Conflict at {slot_label}: " + "; ".join(labels))
        return warnings

    def complete_task(self, task_id: str) -> None:
        """Mark a task complete; if recurrence_days > 0, append the next occurrence to the same pet."""
        for pet in self.owner.pets:
            for t in pet.tasks:
                if t.task_id == task_id:
                    t.mark_complete()
                    nxt = t.create_next_recurring_task()
                    if nxt is not None:
                        pet.add_task(nxt)
                    self._refresh_queue()
                    return
        raise ValueError(f"No task with id {task_id!r} found.")
