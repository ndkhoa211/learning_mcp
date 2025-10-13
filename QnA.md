## 1. Why cancel pending tasks if response was successful?

In most successful cases, there are NO pending tasks - the code is defensive/precautionary. However, pending tasks can exist even after success in these scenarios:

- Background tasks spawned by the MCP server connection that weren't explicitly awaited
- Cleanup callbacks or timers registered during the session
- Connection monitoring tasks from ClientSession that run in the background
- Incomplete futures from the stdio streams (read/write operations)

The finally block ensures complete cleanup regardless of execution path - it's a safety net to prevent resource leaks, especially important since we're creating a new event loop each time instead of reusing one.

---

## 2. Why is it called "event loop"? What makes it a loop?

The "loop" cycles through:
- Checking if any I/O operations completed (network, file reads)
- Running callbacks/coroutines that are ready
- Checking timers and scheduled tasks
- Repeating until all tasks finish

That's why run_until_complete() blocks - it keeps the loop spinning until your async function finishes!