# Stability Phase 1

Working branch: `fix-core-stability`

## Completed

- Fixed `backend/core/tool_executor.py` by importing `Callable` from `typing`.

## Confirmed next bug

`autonomous/automation_worker.py` has a context initialization bug in `_execute_queue_item`.

The tool-execution branch can reach shared logging code that reads `context.started_at`, but `context` is only created in the legacy handler branch.

## Required direct fix

Inside `_execute_queue_item`, after the task is successfully marked in progress and before this line:

```python
# Check if this is a tool-based execution (new format)
```

add:

```python
context = TaskExecutionContext(
    task=task,
    queue_item=queue_item,
    started_at=datetime.utcnow(),
)
```

Then remove the duplicate context creation inside the legacy handler branch.

## Validation commands

```bash
python -m compileall backend autonomous
python -c "from backend.core.tool_executor import ToolExecutor; print('ToolExecutor import ok')"
```

After the worker patch:

```bash
python -m pytest tests -q
```
