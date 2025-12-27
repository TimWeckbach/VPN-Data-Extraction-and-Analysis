---
description: Set a reminder for the agent to check in future turns
---
1. Parse the user's request to identify the "Task" and the "Condition" (Time or Event).
2. Read the current `reminders.json` file (if it exists) from the root of the workspace.
3. Add a new entry to the list of reminders.
   - Format: `{"id": <uuid>, "task": "<description>", "condition": "<time_or_event_description>", "status": "pending"}`
4. Save the updated list back to `reminders.json`.
5. Confirm to the user that the reminder has been set.

**Note:** The agent must proactively check `reminders.json` and the status of the condition (e.g., check current time via `time-server` or check process status) at the beginning of future turns.
