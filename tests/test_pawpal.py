"""Automated tests for PawPal+ (`pawpal_system`).

Core behaviors covered (happy paths + edge cases):

1. Task lifecycle: mark_complete, add_task on Pet.
2. Sorting: tasks ordered chronologically by due_at.
3. Filtering: by TaskStatus and by pet name substring.
4. Recurrence: completing a daily task spawns the next occurrence on the following day.
5. Conflicts: duplicate (same calendar minute) times yield warning strings, not exceptions.
6. Edge: pet/owner with no tasks still yields safe empty results from scheduler helpers.
"""

from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus, TaskType


def test_mark_complete_changes_status() -> None:
    """Calling mark_complete() sets the task status to completed."""
    task = Task(
        task_id="x1",
        title="Walk",
        description="Quick walk",
        type=TaskType.WALKING,
        due_at=datetime(2026, 4, 9, 9, 0),
        pet_id="p1",
    )
    assert task.status == TaskStatus.PENDING
    task.mark_complete()
    assert task.status == TaskStatus.COMPLETED


def test_add_task_increases_pet_task_count() -> None:
    """Adding a task to a pet increases that pet's task list length."""
    pet = Pet(
        pet_id="p1",
        name="Rex",
        species="dog",
        breed="mix",
        age=3,
        weight=20.0,
        medical_notes="",
        owner_id="o1",
    )
    assert len(pet.tasks) == 0
    task = Task(
        task_id="t1",
        title="Feed",
        description="Breakfast",
        type=TaskType.FEEDING,
        due_at=datetime(2026, 4, 9, 7, 0),
        pet_id=pet.pet_id,
    )
    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert pet.tasks[0] is task


def test_sort_by_time_orders_chronologically() -> None:
    """Sorting correctness: tasks are returned in chronological order by due_at."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    pet = Pet("p1", "Rex", "dog", "x", 1, 10.0, "", "o1")
    owner.add_pet(pet)
    sched = Scheduler("s1", owner)
    t_late = Task("a", "Late", "", TaskType.PLAYTIME, datetime(2026, 5, 1, 18, 0), "p1")
    t_early = Task("b", "Early", "", TaskType.WALKING, datetime(2026, 5, 1, 8, 0), "p1")
    sched.add_task(t_late)
    sched.add_task(t_early)
    ordered = sched.sort_by_time()
    assert [x.task_id for x in ordered] == ["b", "a"]
    times = [x.due_at for x in ordered]
    assert times == sorted(times)


def test_filter_by_status_and_pet_name() -> None:
    """Filtering by status and pet name returns expected subsets."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    dog = Pet("p1", "Max", "dog", "x", 2, 20.0, "", "o1")
    cat = Pet("p2", "Luna", "cat", "y", 1, 5.0, "", "o1")
    owner.add_pet(dog)
    owner.add_pet(cat)
    sched = Scheduler("s1", owner)
    d = datetime(2026, 6, 1, 10, 0)
    t1 = Task("t1", "Walk", "", TaskType.WALKING, d, "p1")
    t2 = Task("t2", "Feed", "", TaskType.FEEDING, d, "p2")
    sched.add_task(t1)
    sched.add_task(t2)
    t1.mark_complete()
    pending = sched.filter_by_status(TaskStatus.PENDING)
    assert len(pending) == 1 and pending[0].task_id == "t2"
    max_tasks = sched.filter_by_pet_name("max")
    assert len(max_tasks) == 1 and max_tasks[0].task_id == "t1"


def test_detect_time_conflicts_flags_duplicate_times() -> None:
    """Conflict detection: scheduler returns warnings when two tasks share the same minute."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    a = Pet("p1", "A", "dog", "x", 1, 10.0, "", "o1")
    b = Pet("p2", "B", "cat", "y", 1, 5.0, "", "o1")
    owner.add_pet(a)
    owner.add_pet(b)
    sched = Scheduler("s1", owner)
    when = datetime(2026, 7, 1, 15, 30)
    sched.add_task(Task("x", "One", "", TaskType.GROOMING, when, "p1"))
    sched.add_task(Task("y", "Two", "", TaskType.PLAYTIME, when, "p2"))
    msgs = sched.detect_time_conflicts(date(2026, 7, 1))
    assert len(msgs) == 1
    assert "Conflict at" in msgs[0]
    assert "One" in msgs[0] and "Two" in msgs[0]


def test_no_conflicts_when_times_differ_by_one_minute() -> None:
    """Edge case: tasks one minute apart do not count as the same slot."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    pet = Pet("p1", "Solo", "dog", "x", 1, 10.0, "", "o1")
    owner.add_pet(pet)
    sched = Scheduler("s1", owner)
    day = date(2026, 9, 1)
    sched.add_task(Task("a", "A", "", TaskType.WALKING, datetime(2026, 9, 1, 10, 0), "p1"))
    sched.add_task(Task("b", "B", "", TaskType.FEEDING, datetime(2026, 9, 1, 10, 1), "p1"))
    assert sched.detect_time_conflicts(day) == []


def test_daily_recurrence_next_task_is_following_day() -> None:
    """Recurrence: completing a daily task creates the next occurrence on the next calendar day."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    pet = Pet("p1", "Rex", "dog", "x", 1, 10.0, "", "o1")
    owner.add_pet(pet)
    sched = Scheduler("s1", owner)
    original_due = datetime(2026, 8, 1, 9, 0)
    sched.add_task(
        Task(
            "daily1",
            "Meds",
            "pill",
            TaskType.MEDICATION,
            original_due,
            "p1",
            recurrence_days=1,
        )
    )
    sched.complete_task("daily1")
    followups = [t for t in pet.tasks if t.task_id != "daily1" and t.status == TaskStatus.PENDING]
    assert len(followups) == 1
    assert followups[0].due_at.date() == (original_due.date() + timedelta(days=1))
    assert followups[0].due_at.time() == original_due.time()


def test_complete_task_non_recurring_does_not_spawn() -> None:
    """Edge case: one-off task completion does not add another task."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    pet = Pet("p1", "Rex", "dog", "x", 1, 10.0, "", "o1")
    owner.add_pet(pet)
    sched = Scheduler("s1", owner)
    sched.add_task(
        Task("once", "Walk", "", TaskType.WALKING, datetime(2026, 8, 2, 8, 0), "p1", recurrence_days=0)
    )
    sched.complete_task("once")
    assert len(pet.tasks) == 1
    assert pet.tasks[0].status == TaskStatus.COMPLETED


def test_pet_with_no_tasks_empty_scheduler_views() -> None:
    """Edge case: pet with no tasks — sort, filter, conflicts stay empty lists."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    owner.add_pet(Pet("p1", "Empty", "dog", "x", 1, 10.0, "", "o1"))
    sched = Scheduler("s1", owner)
    assert owner.get_all_tasks() == []
    assert sched.sort_by_time() == []
    assert sched.filter_by_status(TaskStatus.PENDING) == []
    assert sched.detect_time_conflicts(date(2026, 1, 1)) == []


def test_get_tasks_for_date_respects_day_boundary() -> None:
    """Tasks on different calendar days are not mixed in get_tasks_for_date."""
    owner = Owner("o1", "A", "B", "e", "p", "addr")
    pet = Pet("p1", "Rex", "dog", "x", 1, 10.0, "", "o1")
    owner.add_pet(pet)
    sched = Scheduler("s1", owner)
    sched.add_task(Task("d1", "A", "", TaskType.WALKING, datetime(2026, 10, 5, 12, 0), "p1"))
    sched.add_task(Task("d2", "B", "", TaskType.FEEDING, datetime(2026, 10, 6, 12, 0), "p1"))
    oct5 = sched.get_tasks_for_date(date(2026, 10, 5))
    assert len(oct5) == 1 and oct5[0].task_id == "d1"
