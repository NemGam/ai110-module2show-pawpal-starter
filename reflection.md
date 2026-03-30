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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a lightweight conflict check that flags tasks only when they start at the exact same HH:MM timestamp. It does not compute full time-range overlap using duration (for example, 08:00-08:30 overlapping 08:20-08:40). This tradeoff is reasonable for this project because it keeps the logic simple and fast, still catches the most obvious collisions, and surfaces warnings without blocking the user from continuing to plan tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
