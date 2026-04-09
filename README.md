# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Features

- **Owner & pets** — Store an `Owner` and multiple `Pet` records with basic profile fields; data persists in **`st.session_state`** while the app runs.
- **Tasks** — Add tasks with type, due **date/time**, priority, optional **recurrence** (one-time, daily, weekly), and duration noted in the description.
- **Sorting by time** — `Scheduler.sort_by_time()` returns tasks ordered by `due_at`; the UI shows a **“Sorted by time only”** tab for today.
- **Filtering** — Pending tasks are listed using `filter_by_status(TaskStatus.PENDING)`.
- **Priority-aware daily schedule** — `get_today_schedule()` / `get_tasks_for_date()` order tasks by time, then higher priority first.
- **Conflict warnings** — `detect_time_conflicts()` flags multiple tasks on the **same calendar minute**; the UI surfaces this with **error + expandable details** and a short tip (exact-minute check, not duration overlap).
- **Recurring tasks** — Completing a task via `scheduler.complete_task()` spawns the **next occurrence** when `recurrence_days` is 1 (daily) or 7 (weekly).
- **CLI demo** — `python main.py` exercises sorting, filtering, conflicts, and recurrence without the browser.
- **Tests** — `python -m pytest` covers core scheduler behavior (see **Testing PawPal+** below).

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

### Run the app

```bash
streamlit run app.py
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (draft).
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

## Demo

Replace the image path with your own screenshot after you capture the Streamlit UI (e.g. export from your course assets folder).

<a href="/course_images/ai110/pawpal_app.png" target="_blank"><img src="/course_images/ai110/pawpal_app.png" title="PawPal App" width="" alt="PawPal App" class="center-block" /></a>

Local preview: open `uml_final.png` or add a screenshot named `pawpal_app.png` next to this README and change the `src` to a relative path if needed.

