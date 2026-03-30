# PawPal+ Pet Care Scheduler

PawPal+ is a Streamlit app that helps a pet owner organize daily care tasks across multiple pets. The app uses a dedicated backend logic layer so scheduling behavior is testable and reusable outside the UI.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python -m streamlit run app.py`
3. Run CLI demo: `python main.py`

## Features

- Add and manage multiple pets from the UI.
- Schedule tasks by pet with date, time, and recurrence (`once`, `daily`, `weekly`).
- Sort tasks chronologically using scheduler logic.
- Filter tasks by pet and completion status.
- Mark tasks complete and auto-generate next occurrences for recurring tasks.
- Detect schedule conflicts and show warnings in the UI.

## Smarter Scheduling

The scheduler includes lightweight algorithmic helpers:

- **Sorting by time:** Uses task date + `HH:MM` to produce chronological views.
- **Filtering:** Narrows schedules by pet and/or completion state.
- **Recurring task automation:** Completing daily or weekly tasks creates a follow-up task at the next valid date.
- **Conflict detection:** Flags exact same date/time collisions across pets and tasks.

Tradeoff: conflict detection currently checks exact date/time matches only. It does not detect partial overlaps because tasks do not include durations.

## System Design (Mermaid UML)

```mermaid
classDiagram
      class Task {
         +description: str
         +time: str
         +frequency: str
         +due_date: date
         +completed: bool
         +mark_complete() Optional~Task~
         +scheduled_at() datetime
      }

      class Pet {
         +name: str
         +species: str
         +age: int
         +tasks: list~Task~
         +add_task(task: Task) None
         +task_count() int
      }

      class Owner {
         +name: str
         +pets: dict~str, Pet~
         +add_pet(name: str, species: str, age: int) Pet
         +get_pet(name: str) Optional~Pet~
         +all_pets() list~Pet~
      }

      class Scheduler {
         +owner: Owner
         +get_all_tasks(include_completed: bool) list~(str, Task)~
         +sort_by_time(tasks) list~(str, Task)~
         +filter_tasks(pet_name, completed) list~(str, Task)~
         +add_task_to_pet(pet_name: str, task: Task) bool
         +mark_task_complete(pet_name: str, task_index: int) Optional~Task~
         +detect_conflicts() list~str~
         +todays_schedule() list~(str, Task)~
      }

      Owner "1" o-- "many" Pet : has
      Pet "1" o-- "many" Task : contains
      Scheduler "1" --> "1" Owner : manages
      Scheduler ..> Task : sorts/filters
```

## Testing PawPal+

Run all tests with:

`python -m pytest`

Current test coverage includes:

- Task completion state changes
- Task addition behavior
- Chronological sorting
- Daily recurrence generation
- Conflict detection for duplicate date/time tasks

Confidence Level: ★★★★☆ (4/5)

## Demo

<a href="./assets/winning-img.png" target="_blank"><img src='./assets/winning-img.png' title='PawPal App' width='900' alt='PawPal App' class='center-block' /></a>
