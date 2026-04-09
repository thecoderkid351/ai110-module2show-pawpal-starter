# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

User must be able to enter the owner and pet nformation. They should also be able to add additional feeatures like when the pet is doing different actions like walking, feeding, grooming, etc. They should also be able to view the different time constraints. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler mainly tries to focus on the due date, due time, and nmeric prioty. Priority status depends solely on the time the task is due. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
My application triggers when two tasks are due at the same time. Tasks can be mismatched depending on how tasks build up on off of one another. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI to help assist me with the UML diagram. Additionally, I also used it for assistance with streamlit. It was helpful to ask repeating questions to ensure guidelines and rubrics were as followed. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---
At first, the system was someone hardcoded and dependent on exact strings. When dealing with time, it can be time intensive to take care of every instance. 

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tetsted to ensure tasks were accounting from. Moreover, I checked to ensure that tasks were done in order. Addtionally, I filtered the application to ensure there were no bottlenecks.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I believe with the tests that were conducted. The product is fine as a MVP. 
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

It was very vital to test with pytest to ensure that the system was working as expected. Additionally, I took the time to ensure all were efficient accurate. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
N/A



**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
It is very vital to become careful with AI. It is very useful but powerul at the same time. 