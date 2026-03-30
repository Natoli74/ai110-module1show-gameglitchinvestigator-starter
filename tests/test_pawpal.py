from datetime import date, timedelta

from pawpal_system import Owner, Scheduler, Task


def test_task_completion_marks_done():
    task = Task(description="Feed", time="08:00", frequency="once")

    created = task.mark_complete()

    assert task.completed is True
    assert created is None


def test_adding_task_increases_pet_count():
    owner = Owner("Sam")
    pet = owner.add_pet("Milo", "Dog", 3)

    pet.add_task(Task(description="Walk", time="09:00", frequency="daily"))

    assert pet.task_count() == 1


def test_sorting_returns_chronological_order():
    owner = Owner("Sam")
    pet = owner.add_pet("Milo", "Dog", 3)
    pet.add_task(Task(description="Evening walk", time="19:00"))
    pet.add_task(Task(description="Breakfast", time="07:30"))
    pet.add_task(Task(description="Lunch", time="12:00"))

    scheduler = Scheduler(owner)
    sorted_rows = scheduler.sort_by_time(scheduler.get_all_tasks(include_completed=True))

    assert [row[1].description for row in sorted_rows] == [
        "Breakfast",
        "Lunch",
        "Evening walk",
    ]


def test_daily_recurrence_creates_next_day_task():
    owner = Owner("Sam")
    pet = owner.add_pet("Luna", "Cat", 2)
    pet.add_task(Task(description="Daily meds", time="08:00", frequency="daily"))

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete("Luna", 0)

    assert pet.tasks[0].completed is True
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False


def test_conflict_detection_flags_duplicate_times():
    owner = Owner("Sam")
    owner.add_pet("Milo", "Dog", 3)
    owner.add_pet("Luna", "Cat", 2)

    scheduler = Scheduler(owner)
    scheduler.add_task_to_pet("Milo", Task(description="Walk", time="18:00"))
    scheduler.add_task_to_pet("Luna", Task(description="Feed", time="18:00"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]
    assert "18:00" in warnings[0]
