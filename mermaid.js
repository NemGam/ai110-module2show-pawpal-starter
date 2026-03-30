classDiagram
    class Task {
        +string title
        +int duration
        +string priority
        +string category
        +string time
        +string due_at
        +string frequency
        +bool completed
        +mark_complete() void
        +is_recurring() bool
        +create_next_occurrence() Task
        +parse_due_at() datetime|None
        +is_high_priority() bool
        +to_dict() dict
        +from_dict(data) Task
    }

    class Pet {
        +string name
        +string species
        +Task[] tasks
        +add_task(task) void
        +remove_task(title) void
        +get_tasks_by_priority() Task[]
    }

    class Owner {
        +string name
        +Pet[] pets
        +add_pet(pet) void
        +all_tasks() tuple[Pet,Task][]
    }

    class Scheduler {
        +Owner owner
        +tuple[Pet,Task][] schedule
        +generate_plan() Task[]
        +recommend_planning_window(start) string
        +build_time_schedule(window,start) tuple[Pet,Task][]
        +mark_task_complete(pet_name, task_title, task_index) Task
        +detect_time_conflicts() string[]
        +explain_plan() string
        +filter_tasks(completed, pet_name) Task[]
        +sort_by_time() Task[]
        +total_duration() int
    }

    class AppHelpers {
        +format_due_at(due_date, due_time) string
        +resolve_due_datetime(task, reference) datetime
        +complete_task_in_session(pets_data, pet_idx, task_idx) void
        +remove_task_in_session(pets_data, pet_idx, task_idx) void
        +render_task_card(row, pets_data, pet_idx, task_idx, card_key) void
    }

    Owner "1" --> "0..*" Pet : manages
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "0..*" Task : selects
    AppHelpers ..> Task : uses
    AppHelpers ..> Owner : builds
    AppHelpers ..> Pet : builds
    AppHelpers ..> Scheduler : orchestrates
