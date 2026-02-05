# Fixes for Test Run #2 Stability

This document outlines the critical fixes applied to the Earnetics backend to resolve crashes observed during the second autonomy loop test run.

## 🐛 Issues Fixed

1.  **`KeyError: 'created_at'` in Autonomy Loops**
    *   **Cause:** Jobs/Streams/Directives were being created without a mandatory timestamp, causing the scheduler and review loops to crash when sorting.
    *   **Fix:** Added default `created_at = datetime.utcnow()` hooks in `CorporateMemory.create_task` and `CorporateMemory.create_objective` to ensure no record is ever saved without it.

2.  **`NameError: name 'MAX_ACTIVE_EXPERIMENTS' is not defined`**
    *   **Cause:** The Strategy Runner was referencing a config constant that wasn't imported or defined.
    *   **Fix:** Defined `MAX_ACTIVE_EXPERIMENTS = 3` (configurable via .env) in `strategy_runner.py`.

3.  **`OLLAMA_GENERATE_ERROR: unsupported operand type(s) for +: 'float' and 'str'`**
    *   **Cause:** LLM parameters like `temperature` and `max_tokens` were being passed as strings (from .env) to the Ollama client, which expected numbers.
    *   **Fix:** Explicitly cast `temperature` to `float` and `max_tokens` to `int` in `backend/llm/providers/ollama.py`.

4.  **Robust LLM Architecture**
    *   **Enhancement:** Implemented a new `LLMGateway` with:
        *   **Two-tier routing** (Worker vs Strategist models).
        *   **Concurrency limits** (Semaphore).
        *   **Retries & Timeouts**.
        *   **Structured Error Responses** (Agents don't crash on LLM failure).

## 🛠 Verification

To verify these fixes:

1.  **Check LLM Health:**
    ```bash
    python -m backend.llm.test_gateway
    ```
    *   Ensure all tests pass (Worker, Strategist, Generate Mode).

2.  **Run the Backend:**
    ```bash
    .\scripts\run_all.ps1
    ```
    *   Watch the logs for "Revenue cycle completed" and "Strategy cycle completed".
    *   Ensure no stack traces appear related to `created_at` or `NameError`.

## ⚙️ Configuration (.env)

Ensure your `.env` includes:

```env
# Ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_WORKER_MODEL=llama3.1:8b
OLLAMA_STRATEGIST_MODEL=qwen2.5:14b

# LLM Control
LLM_MAX_CONCURRENCY=2
LLM_TIMEOUT_SECONDS=120
LLM_RETRIES=2
LLM_FALLBACK_TO_WORKER=true

# Strategy
MAX_ACTIVE_EXPERIMENTS=3
```
