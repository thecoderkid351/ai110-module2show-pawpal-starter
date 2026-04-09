"""CLI demo: scheduling algorithms, sorting, filtering, conflicts, recurring tasks."""

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus, TaskType


def format_schedule_line(task: Task, pet_name: str, species: str) -> str:
    """One readable line for a task in the terminal."""
    t = task.due_at.strftime("%H:%M")
    rec = f", every {task.recurrence_days}d" if task.recurrence_days else ""
    return (
        f"  {t}  |  {pet_name} ({species})  |  {task.title}  -  {task.description}"
        f"  [{task.status.value}{rec}]"
    )


def main() -> None:
    owner = Owner(
        owner_id="o1",
        first_name="Alex",
        last_name="Rivera",
        email="alex@example.com",
        phone="555-0100",
        address="123 Oak St",
    )

    pet_max = Pet(
        pet_id="p1",
        name="Max",
        species="dog",
        breed="Lab mix",
        age=4,
        weight=28.5,
        medical_notes="",
        owner_id=owner.owner_id,
    )
    pet_luna = Pet(
        pet_id="p2",
        name="Luna",
        species="cat",
        breed="Domestic shorthair",
        age=2,
        weight=4.2,
        medical_notes="",
        owner_id=owner.owner_id,
    )

    owner.add_pet(pet_max)
    owner.add_pet(pet_luna)

    today = date.today()
    scheduler = Scheduler("sched_demo", owner)

    # Add tasks out of chronological order on purpose
    t_evening = datetime.combine(today, time(18, 45))
    t_morning = datetime.combine(today, time(8, 0))
    t_noon = datetime.combine(today, time(12, 30))
    t_conflict_a = datetime.combine(today, time(15, 0))
    t_conflict_b = datetime.combine(today, time(15, 0))

    out_of_order = [
        Task(
            task_id="t_evening",
            title="Training",
            description="Recall practice",
            type=TaskType.TRAINING,
            due_at=t_evening,
            pet_id=pet_max.pet_id,
            priority=1,
        ),
        Task(
            task_id="t_morning",
            title="Morning walk",
            description="30 min loop",
            type=TaskType.WALKING,
            due_at=t_morning,
            pet_id=pet_max.pet_id,
            priority=2,
        ),
        Task(
            task_id="t_noon",
            title="Feeding",
            description="Wet food",
            type=TaskType.FEEDING,
            due_at=t_noon,
            pet_id=pet_luna.pet_id,
            priority=3,
        ),
        Task(
            task_id="t_daily",
            title="Medication",
            description="Evening pill",
            type=TaskType.MEDICATION,
            due_at=datetime.combine(today, time(20, 0)),
            pet_id=pet_luna.pet_id,
            recurrence_days=1,
            priority=3,
        ),
        Task(
            task_id="t_overlap_1",
            title="Groom brush",
            description="Quick brush",
            type=TaskType.GROOMING,
            due_at=t_conflict_a,
            pet_id=pet_max.pet_id,
            priority=1,
        ),
        Task(
            task_id="t_overlap_2",
            title="Play session",
            description="Fetch",
            type=TaskType.PLAYTIME,
            due_at=t_conflict_b,
            pet_id=pet_luna.pet_id,
            priority=2,
        ),
    ]

    for task in out_of_order:
        scheduler.add_task(task)

    pet_by_id = {p.pet_id: p for p in owner.pets}
    all_tasks = owner.get_all_tasks()

    print()
    print("=== Added tasks (insertion order was non-chronological) ===")
    for task in all_tasks:
        p = pet_by_id[task.pet_id]
        print(format_schedule_line(task, p.name, p.species))

    print()
    print("=== sort_by_time() (chronological) ===")
    for task in scheduler.sort_by_time():
        p = pet_by_id[task.pet_id]
        print(format_schedule_line(task, p.name, p.species))

    print()
    print("=== filter_by_status(PENDING) ===")
    for task in scheduler.filter_by_status(TaskStatus.PENDING):
        p = pet_by_id[task.pet_id]
        print(format_schedule_line(task, p.name, p.species))

    print()
    print('=== filter_by_pet_name("max") ===')
    for task in scheduler.filter_by_pet_name("max"):
        p = pet_by_id[task.pet_id]
        print(format_schedule_line(task, p.name, p.species))

    print()
    print("=== Conflict detection (same day + same hour:minute) ===")
    conflicts = scheduler.detect_time_conflicts(today)
    if not conflicts:
        print("  (none)")
    else:
        for msg in conflicts:
            print(f"  WARNING: {msg}")

    print()
    print("=== Complete daily task -> next occurrence (recurrence_days=1) ===")
    before_ids = {t.task_id for t in pet_luna.tasks}
    scheduler.complete_task("t_daily")
    after_tasks = pet_luna.tasks
    new_ones = [t for t in after_tasks if t.task_id not in before_ids and t.status == TaskStatus.PENDING]
    print(f"  Completed t_daily; new pending follow-up task(s): {len(new_ones)}")
    for t in new_ones:
        print(f"    -> {t.title} @ {t.due_at.isoformat(timespec='minutes')}")

    print()
    print(f"=== Today's schedule ({today.isoformat()}) ===")
    schedule = scheduler.get_today_schedule(today)
    if not schedule:
        print("  (no tasks today)")
    else:
        for task in schedule:
            p = pet_by_id[task.pet_id]
            print(format_schedule_line(task, p.name, p.species))
    print()


if __name__ == "__main__":
    main()
