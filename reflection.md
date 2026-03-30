# PawPal+ Project Reflection

## 1. System Design

- User should be able to see the schedule for today
- User should be able to assign constraints and priorities
- User should be able to change schedule for today


**a. Initial design**

- Briefly describe your initial UML design.

### **Task**
Represents a single pet care activity.

#### Attributes:

- **title** - name of the task (e.g., "Morning walk")
- **duration** - how many minutes it takes
- **priority** - importance level (high / medium / low)
- **category** - type of care (walk, feeding, meds, grooming, enrichment)
- **completed** - whether it's been done today
#### Methods:
- **is_high_priority()** - returns True if priority is high
- **to_dict() / from_dict()** - for serialization (Streamlit session state)



### **Pet**
Represents the animal being cared for.

#### Attributes:
- **name** - pet's name
- **species** - dog, cat, or other
- **tasks** - list of Task objects assigned to this pet

#### Methods:
- **add_task(task)** - adds a task to the list
- **remove_task(title)** - removes a task by name
- **get_tasks_by_priority()** - returns tasks sorted by priority



### **Owner**
Represents the person managing the pet's care.

#### Attributes:
- **name** - owner's name
- **pets** - list of Pet objects



### **Scheduler**
Produces a daily care plan based on constraints and priorities.

#### Attributes:
- **owner** - the Owner (gives access to pet tasks)
- **schedule** - ordered list of scheduled tasks

#### Methods:
- **generate_plan()** - picks and orders incomplete tasks by priority
- **explain_plan()** - returns a human-readable explanation of why each task was included or excluded
- **total_duration()** - sum of all scheduled task durations


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers several practical constraints:
- Completed status: completed tasks are excluded from scheduling.
- Priority: high-priority tasks are ordered before medium and low.
- Time and due date: tasks are sorted by due time, with overdue items surfaced first.
- Planning window: only tasks inside the selected weekly or monthly horizon are included.
- Recurrence frequency: daily and weekly tasks roll forward after completion so routines remain active.
- Multi-pet scope: tasks are scheduled across all pets for the same owner in one global plan.

I prioritized constraints based on correctness and day-to-day usability. First, completed tasks must be excluded so the plan does not repeat finished work. Next, urgency and importance (due time plus priority) determine what should happen first. Then, the planning window keeps the output actionable instead of overwhelming. Recurrence handling comes next so regular care tasks stay current without manual re-entry. Preference-style constraints were kept lighter because baseline reliability and urgency ordering were more important for this version.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a lightweight conflict check that flags tasks only when they start at the exact same HH:MM timestamp. It does not compute full time-range overlap using duration (for example, 08:00-08:30 overlapping 08:20-08:40). This tradeoff is reasonable for this project because it keeps the logic simple and fast, still catches the most obvious collisions, and surfaces warnings without blocking the user from continuing to plan tasks.

---

## 3. AI Collaboration

**a. How you used AI**
I brainstormed the design with it and updated README when possible

**b. Judgment and verification**

AI suggested a lot of weird UI changes that didn't work well

---

## 4. Testing and Verification

**a. What you tested**

I tested the core scheduling behaviors end-to-end:
- Task and pet basics: marking a task complete, adding tasks to a pet.
- Priority ordering: high before medium before low, including across multiple pets.
- Completion filtering: completed tasks are excluded from active schedules.
- Recurring logic: daily/weekly recurrence rollover, one-time tasks not duplicating, and due date rollover for recurring tasks.
- Planning-window behavior: weekly vs monthly recommendation based on due-date spread.
- Time-based schedule selection: including multiple tasks on the same day/time horizon.
- Plan explanation: owner name, empty-plan behavior, cumulative offsets, and task time display.
- Conflict detection: warnings for same-time tasks for the same pet and across different pets.

These tests are important because they protect the highest-risk logic paths (ordering, recurrence, filtering, and conflict signaling) that directly affect whether the generated plan is trustworthy for daily use.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am reasonably confident in the current scheduler behavior because the automated test suite covers the major rules and currently passes (24 tests). The implementation handles priority sorting, recurrence rollover, planning windows, and same-time conflict warnings consistently.

If I had more time, I would add edge-case tests for:
- Invalid or malformed `time` / `due_at` inputs and recovery behavior.
- Duration-overlap conflicts (not just exact same start time).
- Boundary-date behavior around month transitions and daylight-saving changes.
- Very large task lists for performance and stability.

---

## 5. Reflection

**a. What went well**

I loved the complexity of this project. It felt really great to be able to tackle an actual engineering challenge.

**b. What you would improve**

Code and UI. I am not very good with streamlit and it feels quite stiff and non flexible

**c. Key takeaway**

It's hard to make a complex system with AI w/o understanding what's going on first
