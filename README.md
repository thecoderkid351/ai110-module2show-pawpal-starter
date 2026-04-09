# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter scheduling

The logic layer (`pawpal_system.py`) includes a **`Scheduler`** that can:

- **`sort_by_time()`** — order tasks by `due_at` (datetime sort, not string times).
- **`filter_by_status()`** / **`filter_by_pet_name()`** — narrow tasks by completion state or pet name substring.
- **Recurring tasks** — `recurrence_days` uses `timedelta`; when you complete a task via **`Scheduler.complete_task()`**, a **next pending** instance is added for daily (`1`) or weekly (`7`) style cadences.
- **`detect_time_conflicts()`** — returns **warning strings** (never raises) if multiple tasks land on the **same day and minute**; the Streamlit app shows these when you click **Generate schedule**.

Try the CLI demo: `python main.py` (tasks added out of order, then sorted/filtered, conflicts printed, daily completion demo).

## Testing PawPal+

Run the automated suite from the project root:

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover:

- **Task / Pet basics** — `mark_complete`, adding a task increases count.
- **Sorting** — `Scheduler.sort_by_time()` returns tasks in chronological order by `due_at`.
- **Filtering** — by completion status and by pet name substring.
- **Conflict detection** — duplicate same-minute slots produce warning strings; nearby minutes do not.
- **Recurrence** — completing a **daily** (`recurrence_days=1`) task creates a **next-day** pending follow-up; non-recurring tasks do not spawn copies.
- **Edge cases** — owner with a pet but **no tasks** yields empty sorts/filters/conflicts; `get_tasks_for_date` only includes the requested calendar day.

**Confidence:** ★★★★☆ (4/5) — Core flows and the main scheduler edge cases above are covered; the suite does not yet model overlapping task **durations** or full UI/session-state integration tests.
