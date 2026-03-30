from datetime import date, timedelta

from pawpal_system import Owner, Scheduler, Task


def print_schedule(title: str, schedule_rows: list[tuple[str, Task]]) -> None:
    """Print an aligned schedule table for terminal readability."""
    print(f"\n{title}")
    print("-" * len(title))
    if not schedule_rows:
        print("No tasks found.")
        return

    print(f"{'Pet':<12} {'Date':<12} {'Time':<6} {'Status':<10} Description")
    print("-" * 60)
    for pet_name, task in schedule_rows:
        status = "Done" if task.completed else "Pending"
        print(
            f"{pet_name:<12} {task.due_date.isoformat():<12} "
            f"{task.time:<6} {status:<10} {task.description} ({task.frequency})"
        )


def build_demo() -> Scheduler:
    """Seed an owner with pets and tasks for CLI validation."""
    owner = Owner("Alex")
    owner.add_pet("Milo", "Dog", 4)
    owner.add_pet("Luna", "Cat", 2)

    scheduler = Scheduler(owner)

    scheduler.add_task_to_pet(
        "Milo",
        Task(description="Morning walk", time="08:30", frequency="daily"),
    )
    scheduler.add_task_to_pet(
        "Milo",
        Task(description="Dinner", time="18:00", frequency="daily"),
    )
    scheduler.add_task_to_pet(
        "Luna",
        Task(description="Litter cleaning", time="07:45", frequency="daily"),
    )
    scheduler.add_task_to_pet(
        "Luna",
        Task(description="Vet vitamins", time="18:00", frequency="weekly"),
    )

    # Add one task for tomorrow to demonstrate date-aware sorting.
    scheduler.add_task_to_pet(
        "Milo",
        Task(
            description="Nail trim",
            time="09:15",
            frequency="once",
            due_date=date.today() + timedelta(days=1),
        ),
    )

    return scheduler


if __name__ == "__main__":
    scheduler = build_demo()

    print_schedule("Today's Schedule", scheduler.todays_schedule())

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nConflict Warnings")
        print("-----------------")
        for warning in conflicts:
            print(f"- {warning}")
    else:
        print("\nNo scheduling conflicts detected.")
