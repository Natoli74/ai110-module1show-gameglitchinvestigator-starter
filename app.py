from datetime import date

import streamlit as st

from pawpal_system import Owner, Scheduler, Task


def init_state() -> None:
    """Initialize and persist Owner and Scheduler objects in session state."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="PawPal User")
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler(st.session_state.owner)


def rows_to_table(rows: list[tuple[str, Task]]) -> list[dict[str, str]]:
    """Convert task rows to table-friendly dictionaries."""
    data: list[dict[str, str]] = []
    for pet_name, task in rows:
        data.append(
            {
                "Pet": pet_name,
                "Date": task.due_date.isoformat(),
                "Time": task.time,
                "Task": task.description,
                "Frequency": task.frequency,
                "Completed": "Yes" if task.completed else "No",
            }
        )
    return data


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
init_state()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling with sorting, filtering, recurrence, and conflict warnings.")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Add a Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.text_input("Species", value="Dog")
        age = st.number_input("Age", min_value=0, max_value=40, value=1, step=1)
        add_pet_clicked = st.form_submit_button("Add Pet")

    if add_pet_clicked:
        if not pet_name.strip():
            st.error("Please provide a pet name.")
        else:
            owner.add_pet(pet_name.strip(), species.strip() or "Unknown", int(age))
            st.success(f"Added pet: {pet_name.strip()}")

with right_col:
    st.subheader("Schedule a Task")
    pet_options = list(owner.pets.keys())
    if not pet_options:
        st.info("Add at least one pet before scheduling tasks.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            selected_pet = st.selectbox("Pet", options=pet_options)
            description = st.text_input("Task description", value="Walk")
            task_time = st.time_input("Task time")
            due_date = st.date_input("Due date", value=date.today())
            frequency = st.selectbox("Frequency", options=["once", "daily", "weekly"])
            add_task_clicked = st.form_submit_button("Add Task")

        if add_task_clicked:
            if not description.strip():
                st.error("Please provide a task description.")
            else:
                task = Task(
                    description=description.strip(),
                    time=task_time.strftime("%H:%M"),
                    frequency=frequency,
                    due_date=due_date,
                )
                scheduler.add_task_to_pet(selected_pet, task)
                st.success(f"Added task to {selected_pet}: {description.strip()}")

st.divider()
st.subheader("Task Views")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_filter_pet = st.selectbox(
        "Filter by pet",
        options=["All"] + list(owner.pets.keys()),
    )
with filter_col2:
    selected_status = st.selectbox(
        "Filter by completion",
        options=["All", "Pending", "Completed"],
    )

pet_filter = None if selected_filter_pet == "All" else selected_filter_pet
completed_filter = None
if selected_status == "Pending":
    completed_filter = False
elif selected_status == "Completed":
    completed_filter = True

filtered_rows = scheduler.filter_tasks(
    pet_name=pet_filter,
    completed=completed_filter,
)
sorted_rows = scheduler.sort_by_time(filtered_rows)

st.markdown("#### All Tasks (Sorted)")
if sorted_rows:
    st.table(rows_to_table(sorted_rows))
else:
    st.info("No tasks match the selected filters.")

st.markdown("#### Today's Schedule")
today_rows = scheduler.todays_schedule()
if today_rows:
    st.table(rows_to_table(today_rows))
else:
    st.info("No tasks scheduled for today.")

st.markdown("#### Conflict Warnings")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No task time conflicts detected.")

st.divider()
st.subheader("Complete a Task")

if not owner.pets:
    st.info("Add pets and tasks to mark work complete.")
else:
    complete_pet = st.selectbox("Pet for completion", options=list(owner.pets.keys()))
    target_pet = owner.get_pet(complete_pet)

    pending_options: list[str] = []
    pending_index_lookup: dict[str, int] = {}
    if target_pet:
        for idx, task in enumerate(target_pet.tasks):
            if not task.completed:
                label = (
                    f"#{idx} | {task.due_date.isoformat()} {task.time} | "
                    f"{task.description} ({task.frequency})"
                )
                pending_options.append(label)
                pending_index_lookup[label] = idx

    if not pending_options:
        st.info("No pending tasks for this pet.")
    else:
        selected_task_label = st.selectbox("Pending task", options=pending_options)
        if st.button("Mark Complete"):
            next_task = scheduler.mark_task_complete(
                complete_pet,
                pending_index_lookup[selected_task_label],
            )
            st.success("Task marked complete.")
            if next_task:
                st.info(
                    "Recurring task generated for "
                    f"{next_task.due_date.isoformat()} at {next_task.time}."
                )
            st.rerun()
