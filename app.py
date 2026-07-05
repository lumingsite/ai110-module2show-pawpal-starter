import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Initialize session state once per session
if "owner" not in st.session_state:
    st.session_state.owner = None

# --- Step 1: Owner + Pet Profile ---
st.subheader("Step 1: Set Up Profile")

with st.form("profile_form"):
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=60)
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Tabby Cat")
    age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=2)
    special_needs = st.text_input("Special needs (optional)", value="")
    profile_submitted = st.form_submit_button("Save Profile")

if profile_submitted:
    pet = Pet(name=pet_name, breed=breed, age=int(age), special_needs=special_needs)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.success(f"Profile saved for {owner_name} and {pet_name}!")

# --- Step 2: Add Tasks ---
if st.session_state.owner:
    owner = st.session_state.owner
    pet = next(iter(owner.pets.values()))

    st.divider()
    st.subheader("Step 2: Add Tasks")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task name", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    category = st.text_input("Category (e.g. walk, feeding, grooming)", value="walk")
    is_recurring = st.checkbox("Recurring daily?")

    if st.button("Add Task"):
        task = Task(
            name=task_name,
            category=category,
            duration_min=int(duration),
            priority=priority,
            is_recurring=is_recurring,
        )
        pet.add_task(task)
        st.success(f"Added: {task_name}")

    if pet.tasks:
        st.write(f"Tasks for {pet.name}:")
        st.table([
            {
                "Task": t.name,
                "Category": t.category,
                "Duration (min)": t.duration_min,
                "Priority": t.priority,
                "Done": t.is_completed,
            }
            for t in pet.tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

    # --- Step 3: Generate Schedule ---
    st.divider()
    st.subheader("Step 3: Generate Schedule")

    if st.button("Generate Schedule"):
        if not pet.get_pending_tasks():
            st.warning("No pending tasks to schedule. Add tasks above.")
        else:
            scheduler = Scheduler(owner)
            st.text(scheduler.explain())
else:
    st.info("Fill in the profile above to get started.")
