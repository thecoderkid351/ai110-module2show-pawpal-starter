import streamlit as st
from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType


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


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

_ensure_app_state()
owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")

st.markdown(
    """
Plan pet care with your **logic layer**: `Owner`, `Pet`, `Task`, and `Scheduler` live in `pawpal_system.py`
and are kept in **`st.session_state`** so data survives button clicks and reruns.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps an owner track pets and tasks, then build a schedule for a given day.
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
    st.info("No pets yet. Add one below — `Owner.add_pet()` will attach it in memory.")
else:
    for p in owner.pets:
        st.write(f"**{p.name}** ({p.species}, {p.breed}) — {len(p.tasks)} task(s), id `{p.pet_id}`")

st.markdown("### Add a pet")
st.caption("Submitting this form calls **`owner.add_pet(pet)`** so the `Pet` stays on your `Owner` in session state.")
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
            st.success(f"Added **{pet.name}** (`Pet` stored on session `owner`).")
            st.rerun()

st.divider()

st.subheader("Tasks")
st.caption("Adding a task uses **`scheduler.add_task(task)`**, which finds the pet on the owner and appends the `Task`.")

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
            )
            scheduler.add_task(task)
            st.success(f"Task **{task.title}** added for **{chosen.name}**.")
            st.rerun()

st.divider()

st.subheader("Today's schedule")
st.caption("**`scheduler.get_today_schedule()`** pulls tasks from all pets for today, ordered by time then priority.")

if st.button("Generate schedule"):
    today = date.today()
    plan = scheduler.get_today_schedule(today)
    pet_by_id = {p.pet_id: p for p in owner.pets}
    conflicts = scheduler.detect_time_conflicts(today)
    if conflicts:
        for msg in conflicts:
            st.warning(msg)
    if not plan:
        st.info(f"No tasks due on **{today.isoformat()}**.")
    else:
        st.markdown(f"### {today.isoformat()}")
        for t in plan:
            pet = pet_by_id.get(t.pet_id)
            pet_part = f"{pet.name} ({pet.species})" if pet else t.pet_id
            line = (
                f"**{t.due_at.strftime('%H:%M')}** · {pet_part} · **{t.title}** "
                f"— {t.description} · {_priority_label(t.priority)} · `{t.status.value}`"
            )
            st.write(line)
