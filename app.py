import streamlit as st
from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus, TaskType


def _ensure_app_state() -> None:
    """Create Owner and Scheduler once; they persist in st.session_state across reruns."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(
            owner_id="ui_owner_1",
            first_name="Jordan",
            last_name="Rivera",
            email="jordan@example.com",
            phone="",
            address="",
        )
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler("ui_scheduler_1", st.session_state.owner)
    if "_next_pet_id" not in st.session_state:
        st.session_state._next_pet_id = 1
    if "_next_task_id" not in st.session_state:
        st.session_state._next_task_id = 1


def _priority_from_label(label: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(label, 2)


def _priority_label(value: int) -> str:
    return {1: "low", 2: "medium", 3: "high"}.get(value, "medium")


def _recurrence_days_from_choice(choice: str) -> int:
    return {"none": 0, "daily": 1, "weekly": 7}.get(choice, 0)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

_ensure_app_state()
owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")

st.markdown(
    """
Plan pet care with your **logic layer**: `Owner`, `Pet`, `Task`, and `Scheduler` from `pawpal_system.py` are stored in **`st.session_state`**
so data survives reruns. The UI below calls **sorting, filtering, conflict detection, and recurrence** on your `Scheduler`.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps an owner track pets and tasks, build a **priority-aware daily schedule**, and see **warnings** when two tasks land on the same minute.
"""
    )

st.divider()

st.subheader("Owner profile")
c1, c2 = st.columns(2)
with c1:
    fn = st.text_input("First name", value=owner.first_name, key="owner_fn")
with c2:
    ln = st.text_input("Last name", value=owner.last_name, key="owner_ln")
em = st.text_input("Email", value=owner.email, key="owner_em")
ph = st.text_input("Phone", value=owner.phone, key="owner_ph")
ad = st.text_input("Address", value=owner.address, key="owner_ad")
if st.button("Save owner profile"):
    owner.update_contact_info(email=em, phone=ph, address=ad)
    owner.first_name = fn
    owner.last_name = ln
    st.success("Owner profile updated.")
    st.rerun()

st.divider()

st.subheader("Your pets")
if not owner.pets:
    st.info("No pets yet. Add one below.")
else:
    pet_rows = {
        "Name": [p.name for p in owner.pets],
        "Species": [p.species for p in owner.pets],
        "Tasks": [len(p.tasks) for p in owner.pets],
        "Pet ID": [p.pet_id for p in owner.pets],
    }
    st.dataframe(pet_rows, use_container_width=True, hide_index=True)

st.markdown("### Add a pet")
with st.form("add_pet_form"):
    pn = st.text_input("Pet name", value="Mochi")
    sp = st.selectbox("Species", ["dog", "cat", "other"])
    br = st.text_input("Breed", value="mix")
    ag = st.number_input("Age (years)", min_value=0, max_value=40, value=2)
    wt = st.number_input("Weight", min_value=0.0, max_value=200.0, value=5.0, step=0.1)
    notes = st.text_area("Medical notes", value="", height=68)
    add_pet_submit = st.form_submit_button("Add pet")
    if add_pet_submit:
        if not pn.strip():
            st.error("Pet name is required.")
        else:
            pid = f"pet_{st.session_state._next_pet_id}"
            st.session_state._next_pet_id += 1
            pet = Pet(
                pet_id=pid,
                name=pn.strip(),
                species=sp,
                breed=br.strip() or "unknown",
                age=int(ag),
                weight=float(wt),
                medical_notes=notes.strip(),
                owner_id=owner.owner_id,
            )
            owner.add_pet(pet)
            scheduler._refresh_queue()
            st.success(f"Added **{pet.name}**.")
            st.rerun()

st.divider()

st.subheader("Tasks")
if not owner.pets:
    st.warning("Add at least one pet before scheduling tasks.")
else:
    pet_labels = {f"{p.name} ({p.pet_id})": p for p in owner.pets}
    with st.form("add_task_form"):
        pet_choice = st.selectbox("Pet", options=list(pet_labels.keys()))
        t_title = st.text_input("Task title", value="Morning walk")
        t_desc = st.text_input("Description", value="Neighborhood loop")
        t_type = st.selectbox(
            "Task type",
            options=list(TaskType),
            format_func=lambda x: x.name.replace("_", " ").title(),
        )
        d = st.date_input("Due date", value=date.today())
        tm = st.time_input("Due time", value=time(9, 0))
        dur = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        pr = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recur = st.selectbox(
            "Recurrence",
            ["none", "daily", "weekly"],
            format_func=lambda x: {"none": "One-time", "daily": "Daily", "weekly": "Weekly"}[x],
            index=0,
        )
        add_task_submit = st.form_submit_button("Add task")
        if add_task_submit:
            chosen = pet_labels[pet_choice]
            tid = f"task_{st.session_state._next_task_id}"
            st.session_state._next_task_id += 1
            due = datetime.combine(d, tm)
            desc = t_desc.strip()
            if dur:
                desc = f"{desc} ({int(dur)} min)".strip()
            task = Task(
                task_id=tid,
                title=t_title.strip(),
                description=desc or t_title.strip(),
                type=t_type,
                due_at=due,
                pet_id=chosen.pet_id,
                priority=_priority_from_label(pr),
                recurrence_days=_recurrence_days_from_choice(recur),
            )
            scheduler.add_task(task)
            st.success(f"Task **{task.title}** added for **{chosen.name}**.")
            st.rerun()

    st.markdown("#### Pending tasks (scheduler filter)")
    st.caption("`scheduler.filter_by_status(TaskStatus.PENDING)`")
    pending = scheduler.filter_by_status(TaskStatus.PENDING)
    pet_by_id = {p.pet_id: p for p in owner.pets}
    if not pending:
        st.info("No pending tasks.")
    else:
        pend_rows = {
            "Time": [t.due_at.strftime("%Y-%m-%d %H:%M") for t in pending],
            "Pet": [pet_by_id[t.pet_id].name if t.pet_id in pet_by_id else t.pet_id for t in pending],
            "Title": [t.title for t in pending],
            "Priority": [_priority_label(t.priority) for t in pending],
            "Recurrence (days)": [t.recurrence_days for t in pending],
        }
        st.dataframe(pend_rows, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Today's schedule & insights")
st.caption(
    "Uses **`get_today_schedule()`** (time + priority) and **`sort_by_time()`** (chronological). "
    "Conflicts use **`detect_time_conflicts()`** — shown prominently so you can reschedule."
)

today = date.today()
pet_by_id = {p.pet_id: p for p in owner.pets}

if st.button("Generate schedule & check conflicts", type="primary"):
    plan = scheduler.get_today_schedule(today)
    sorted_today = [t for t in scheduler.sort_by_time() if t.due_at.date() == today]
    conflicts = scheduler.detect_time_conflicts(today)

    if conflicts:
        st.error("**Time overlap detected** — two or more tasks share the same clock minute today.")
        st.caption(
            "Tip: change one task’s time by a few minutes, or merge activities when possible. "
            "This check is exact-minute only (it does not estimate duration overlap)."
        )
        with st.expander("Conflict details (read-only)", expanded=True):
            for msg in conflicts:
                st.warning(msg)
    else:
        st.success(f"No same-minute conflicts for **{today.isoformat()}**.")

    tab1, tab2 = st.tabs(["Priority-aware schedule", "Sorted by time only"])
    with tab1:
        if not plan:
            st.info(f"No tasks due on **{today.isoformat()}**.")
        else:
            rows = {
                "Time": [t.due_at.strftime("%H:%M") for t in plan],
                "Pet": [pet_by_id[t.pet_id].name if t.pet_id in pet_by_id else t.pet_id for t in plan],
                "Task": [t.title for t in plan],
                "Description": [t.description[:40] + "…" if len(t.description) > 40 else t.description for t in plan],
                "Priority": [_priority_label(t.priority) for t in plan],
                "Status": [t.status.value for t in plan],
            }
            st.dataframe(rows, use_container_width=True, hide_index=True)

    with tab2:
        if not sorted_today:
            st.info("No tasks today to sort.")
        else:
            rows2 = {
                "Time": [t.due_at.strftime("%H:%M") for t in sorted_today],
                "Pet": [pet_by_id[t.pet_id].name if t.pet_id in pet_by_id else t.pet_id for t in sorted_today],
                "Task": [t.title for t in sorted_today],
                "Status": [t.status.value for t in sorted_today],
            }
            st.dataframe(rows2, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Mark task complete")
st.caption(
    "Calls **`scheduler.complete_task(task_id)`**. Daily/weekly recurring tasks automatically get a **next occurrence**."
)
if not owner.pets or not owner.get_all_tasks():
    st.info("Add tasks above to enable completion.")
else:
    all_tasks = owner.get_all_tasks()
    label_to_task = {f"{t.due_at.strftime('%m/%d %H:%M')} · {pet_by_id[t.pet_id].name if t.pet_id in pet_by_id else '?'} · {t.title} ({t.task_id})": t for t in all_tasks}
    pick = st.selectbox("Task", options=list(label_to_task.keys()))
    if st.button("Mark selected complete"):
        t = label_to_task[pick]
        scheduler.complete_task(t.task_id)
        st.success(f"Completed **{t.title}**. If recurring, a follow-up task was added.")
        st.rerun()
