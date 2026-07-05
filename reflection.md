# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core user actions:
1. A user can set up their profile by entering their name, their pet's name and breed, and how much time they have available each day.
2. A user can add or edit care tasks for their pet, such as walks, feeding, medication, or grooming, and specify how long each task takes and how important it is.
3. A user can generate a daily care plan that automatically schedules tasks based on their priorities and time constraints, and see an explanation of why the plan was arranged that way.

My initial design has four classes:

- **Owner** — holds the user's name and how many minutes per day they have available for pet care. An Owner has exactly one Pet and a list of Tasks.
- **Pet** — holds the pet's name, breed, age, and any special needs.
- **Task** — represents a single care activity (walk, feeding, meds, grooming, etc.). It stores the task name, category, how long it takes in minutes, its priority level (high/medium/low), and whether it recurs daily.
- **Scheduler** — the core logic class. It receives the Owner's available time and their list of Tasks, then sorts tasks by priority, filters out tasks that won't fit in the remaining time, assigns start times, and returns an ordered schedule with a plain-language explanation of why the plan was arranged the way it was. It also handles two edge cases internally: (1) if total task time exceeds available time, it drops the lowest-priority tasks and notes what was skipped; (2) if a single task is longer than the total available time, it warns the user and skips that task.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

Yes, the design changed after reviewing the initial skeleton.

The most significant change was adding cached state to `Scheduler`. The original design had `explain()` as a standalone method with no stored data, which would have forced it to re-run the entire sort-filter-schedule pipeline every time it was called. To fix this, `Scheduler` now stores `_schedule` and `_skipped` after the first call to `generate_schedule()`, so `explain()` can reuse those results without recomputing.

A smaller change was adding `__post_init__` validation to `Task`. The original skeleton accepted any string for `priority`, which would allow silent bugs if an invalid value like `"urgent"` was passed. The validation now raises a `ValueError` immediately if the priority is not `"high"`, `"medium"`, or `"low"`, making the error obvious at the point of creation rather than at scheduling time.

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

`filter_by_time` fills the day strictly in priority order (high → medium → low), not by optimal packing. If a 55-minute high-priority task and a 60-minute budget leave 5 minutes free, three quick 5-minute low-priority tasks that would've collectively fit better get skipped rather than displacing the high-priority one — a knapsack-style packer maximizing total tasks scheduled would sometimes reorder that. I chose strict-priority-order instead, because for a pet owner "why did the schedule drop my dog's vet-adjacent task and keep grooming?" is a worse experience than "you didn't have enough time for the low-priority stuff today" — priority order is predictable and matches what the owner explicitly told the app mattered most, even when it isn't the mathematically densest packing of the available minutes.

A related, smaller tradeoff: `detect_conflicts` only flags overlaps between tasks that have an explicit fixed `time` (e.g., a vet appointment at `14:30`). Tasks without a set time are treated as flexible and never checked against each other for overlap, since the scheduler is free to place them anywhere in sequence. This keeps conflict detection cheap (one sort + linear sweep over just the timed subset) and avoids false-positive warnings on tasks that were never meant to happen at a specific clock time.

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
