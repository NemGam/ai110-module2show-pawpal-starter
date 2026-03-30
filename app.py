import streamlit as st
from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Task, Scheduler


def format_due_at(due_date: date, due_time: time) -> str:
    """Return a compact due timestamp in YYYY-MM-DD HH:MM."""
    return datetime.combine(due_date, due_time).strftime("%Y-%m-%d %H:%M")


def resolve_due_datetime(task: Task, reference: datetime | None = None) -> datetime:
    """Return a concrete due datetime, defaulting to reference day + task HH:MM."""
    anchor = reference or datetime.now()
    parsed = task.parse_due_at()
    if parsed is not None:
        return parsed

    try:
        hour, minute = task.time.split(":")
        return anchor.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
    except (ValueError, TypeError):
        return anchor


def complete_task_in_session(pets_data: list[dict], pet_idx: int, task_idx: int) -> None:
    """Mark a task complete and roll recurring tasks forward in place."""
    existing_task = pets_data[pet_idx]["tasks"][task_idx]
    if existing_task.get("completed", False):
        return

    frequency = existing_task.get("frequency", "once")
    if frequency in {"daily", "weekly"}:
        rolled_forward = Task.from_dict(existing_task).create_next_occurrence().to_dict()
        pets_data[pet_idx]["tasks"][task_idx] = rolled_forward
        return

    pets_data[pet_idx]["tasks"][task_idx] = {**existing_task, "completed": True}


def remove_task_in_session(pets_data: list[dict], pet_idx: int, task_idx: int) -> None:
    """Remove a task from the selected pet's task list by index."""
    tasks = pets_data[pet_idx].get("tasks", [])
    if 0 <= task_idx < len(tasks):
        tasks.pop(task_idx)


def render_task_card(
    row: dict,
    pets_data: list[dict],
    pet_idx: int,
    task_idx: int,
    card_key: str,
) -> None:
    """Render one scheduled task as a card with a completion action."""
    due_label = row["due_at"] if row["due_at"] else row["time"]
    with st.container(border=True):
        top_left, top_right = st.columns([4, 3])
        with top_left:
            st.markdown(f"**{row['title']}**")
            st.caption(f"{row['pet_name']} ({row['species']}) | {row['category']} | {row['due_bucket']}")
        with top_right:
            action_col1, action_col2 = st.columns([3, 2])
            with action_col1:
                if st.button("Mark complete", key=f"{card_key}_complete", use_container_width=True):
                    complete_task_in_session(pets_data, pet_idx, task_idx)
                    st.rerun()
            with action_col2:
                if st.button("Remove", key=f"{card_key}_remove", use_container_width=True):
                    remove_task_in_session(pets_data, pet_idx, task_idx)
                    st.rerun()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.caption("Due")
            st.write(due_label)
        with c2:
            st.caption("Priority")
            st.write(row["priority"].upper())
        with c3:
            st.caption("Duration")
            st.write(f"{row['duration']} min")
        with c4:
            st.caption("Frequency")
            st.write(row["frequency"])


st.set_page_config(page_title="PawPal+", page_icon="P", layout="centered")
st.title("PawPal+")

# ---------------------------------------------------------------------------
# Session-state bootstrap
# ---------------------------------------------------------------------------
if "owners" not in st.session_state:
    st.session_state.owners = [{"name": "Jordan", "pets": []}]
if "pet_idx" not in st.session_state:
    st.session_state.pet_idx = 0

# ---------------------------------------------------------------------------
# Owner bar
# ---------------------------------------------------------------------------
st.subheader("Owner")
owner_data = st.session_state.owners[0]
new_name = st.text_input("Owner name", value=owner_data["name"], key="owner_name_edit")
if new_name != owner_data["name"]:
    owner_data["name"] = new_name

st.divider()

# ---------------------------------------------------------------------------
# Pet bar
# ---------------------------------------------------------------------------
st.subheader("Pet")

pets = owner_data["pets"]

if not pets:
    st.info("No pets yet. Add one below.")
else:
    st.caption("Current pets")
    for i, pet in enumerate(pets, start=1):
        st.write(f"{i}. {pet['name']} ({pet.get('species', 'other')})")

with st.expander("Add new pet"):
    new_pet_name_inp = st.text_input("Pet name", key="new_pet_name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    if st.button("Add pet"):
        if new_pet_name_inp.strip():
            updated_pets = [
                *pets,
                {"name": new_pet_name_inp.strip(), "species": new_pet_species, "tasks": []},
            ]
            st.session_state.owners[0]["pets"] = updated_pets
            st.session_state.pet_idx = len(updated_pets) - 1
            st.rerun()
        else:
            st.warning("Pet name cannot be empty.")

st.divider()

# ---------------------------------------------------------------------------
# Unified planner (task list + schedule)
# ---------------------------------------------------------------------------
st.subheader("Task Planner")

if not pets:
    st.info("Add a pet first to manage tasks.")
else:
    st.session_state.pet_idx = min(st.session_state.pet_idx, len(pets) - 1)
    pet_options = list(range(len(pets)))
    selected_pet_idx = st.selectbox(
        "Pet for new task",
        pet_options,
        index=st.session_state.pet_idx,
        format_func=lambda i: f"{pets[i]['name']} ({pets[i].get('species', 'other')})",
    )
    st.session_state.pet_idx = selected_pet_idx
    pet_data = pets[selected_pet_idx]
    pet_data.setdefault("tasks", [])

    add_col1, add_col2, add_col3, add_col4, add_col5, add_col6, add_col7 = st.columns(7)
    with add_col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with add_col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with add_col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with add_col4:
        category = st.text_input("Category", value="exercise")
    with add_col5:
        task_date = st.date_input("Date", value=date.today())
    with add_col6:
        task_due_time = st.time_input("Time", value=time(hour=8, minute=0), step=300)
    with add_col7:
        task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

    if st.button("Add task"):
        due_at = format_due_at(task_date, task_due_time)
        pet_data["tasks"].append(
            {
                "title": task_title,
                "duration": int(duration),
                "priority": priority,
                "category": category,
                "time": task_due_time.strftime("%H:%M"),
                "due_at": due_at,
                "frequency": task_frequency,
                "completed": False,
            }
        )
        st.rerun()

    planning_window_label = st.selectbox(
        "Planning window",
        ["auto (recommended)", "weekly", "monthly"],
        index=0,
        help="Auto chooses weekly or monthly based on how far upcoming due tasks are spread.",
    )
    window_value = "auto" if planning_window_label.startswith("auto") else planning_window_label

    owner = Owner(name=owner_data["name"])
    for pet_idx, p in enumerate(pets):
        pet_obj = Pet(name=p["name"], species=p.get("species", "other"))
        for task_idx, t in enumerate(p.get("tasks", [])):
            task_obj = Task(
                title=t["title"],
                duration=t["duration"],
                priority=t["priority"],
                category=t["category"],
                time=t.get("time", "00:00"),
                due_at=t.get("due_at", ""),
                frequency=t.get("frequency", "once"),
                completed=bool(t.get("completed", False)),
            )
            task_obj._ref = (pet_idx, task_idx)
            pet_obj.add_task(task_obj)
        owner.add_pet(pet_obj)

    scheduler = Scheduler(owner=owner)
    recommended_window = scheduler.recommend_planning_window()
    effective_window = recommended_window if window_value == "auto" else window_value
    scheduler.build_time_schedule(window=effective_window)

    if window_value == "auto":
        st.caption(f"Recommended planning window: {recommended_window}")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        show_selected_only = st.checkbox("Show only selected pet", value=True)
    with filter_col2:
        pet_name_filter = st.text_input(
            "Pet name contains",
            placeholder="Type pet name",
            disabled=show_selected_only,
        )

    today = datetime.now().date()
    planned_rows = []
    row_refs = []
    for pet, task in scheduler.schedule:
        due_dt = resolve_due_datetime(task)
        if due_dt.date() < today:
            due_bucket = "overdue"
        elif due_dt.date() == today:
            due_bucket = "today"
        else:
            due_bucket = "upcoming"

        pet_idx, task_idx = task._ref
        planned_rows.append(
            {
                "pet_name": pet.name,
                "species": pet.species,
                "title": task.title,
                "duration": int(task.duration),
                "priority": task.priority,
                "category": task.category,
                "time": task.time,
                "due_at": task.due_at,
                "frequency": task.frequency,
                "due_bucket": due_bucket,
                "completed": bool(task.completed),
            }
        )
        row_refs.append((pet_idx, task_idx))

    filtered_rows = []
    filtered_refs = []
    pet_query = pet_name_filter.strip().lower()
    for row, ref in zip(planned_rows, row_refs):
        if show_selected_only and ref[0] != selected_pet_idx:
            continue
        if pet_query and not show_selected_only and pet_query not in row["pet_name"].lower():
            continue
        filtered_rows.append(row)
        filtered_refs.append(ref)

    conflict_warnings = scheduler.detect_time_conflicts()
    if conflict_warnings:
        st.warning(f"Time conflicts detected: {len(conflict_warnings)}")
        for warning in conflict_warnings:
            st.caption(warning)

    st.caption(f"Total time planned: {scheduler.total_duration()} min")

    if filtered_rows:
        overdue_rows = []
        overdue_refs = []
        today_rows = []
        today_refs = []
        upcoming_rows = []
        upcoming_refs = []

        for row, ref in zip(filtered_rows, filtered_refs):
            if row["due_bucket"] == "overdue":
                overdue_rows.append(row)
                overdue_refs.append(ref)
            elif row["due_bucket"] == "today":
                today_rows.append(row)
                today_refs.append(ref)
            else:
                upcoming_rows.append(row)
                upcoming_refs.append(ref)

        if overdue_rows:
            st.markdown(f"### Overdue ({len(overdue_rows)})")
            for i, row in enumerate(overdue_rows):
                ref_pet_idx, ref_task_idx = overdue_refs[i]
                render_task_card(
                    row=row,
                    pets_data=pets,
                    pet_idx=ref_pet_idx,
                    task_idx=ref_task_idx,
                    card_key=f"card_overdue_{ref_pet_idx}_{ref_task_idx}_{i}",
                )

        st.markdown(f"### Due Today ({len(today_rows)})")
        if today_rows:
            for i, row in enumerate(today_rows):
                ref_pet_idx, ref_task_idx = today_refs[i]
                render_task_card(
                    row=row,
                    pets_data=pets,
                    pet_idx=ref_pet_idx,
                    task_idx=ref_task_idx,
                    card_key=f"card_today_{ref_pet_idx}_{ref_task_idx}_{i}",
                )
        else:
            st.caption("No tasks due today.")

        st.markdown(f"### Upcoming ({len(upcoming_rows)})")
        if upcoming_rows:
            for i, row in enumerate(upcoming_rows):
                ref_pet_idx, ref_task_idx = upcoming_refs[i]
                render_task_card(
                    row=row,
                    pets_data=pets,
                    pet_idx=ref_pet_idx,
                    task_idx=ref_task_idx,
                    card_key=f"card_upcoming_{ref_pet_idx}_{ref_task_idx}_{i}",
                )
        else:
            st.caption("No upcoming tasks.")
    else:
        st.info("No scheduled tasks match the current filters.")

    all_tasks = [task for pet_obj in owner.pets for task in pet_obj.tasks if not task.completed]
    skipped = [t for t in all_tasks if t not in [task for _, task in scheduler.schedule]]
    if skipped:
        st.warning(
            f"Skipped {len(skipped)} task(s) due to planning window limits: "
            + ", ".join(t.title for t in skipped)
        )
