# Earnetics LLM Gateway

This module provides a unified, production-grade gateway for all Local LLM interactions within the Earnetics system. It replaces direct API calls and manages routing, concurrency, and error handling.

## Features

*   **Two-Tier Routing**: Automatically routes tasks to a fast "Worker" model or a smarter "Strategist" model based on the calling agent.
*   **Concurrency Control**: Limits simultaneous LLM requests to prevent system overload (Semaphore).
*   **Resilience**: Built-in retries, timeouts, and fallback mechanisms.
*   **Ollama Integration**: First-class support for Ollama, prioritizing `/api/chat` with a fallback to `/api/generate`.
*   **Structured Logging**: Detailed logs for every attempt, including latency and prompt hashes (privacy-preserving).

## Setup

1.  **Install Ollama**: Download from [ollama.com](https://ollama.com).
2.  **Pull Models**:
    ```bash
    ollama pull llama3.1:8b
    ollama pull qwen2.5:14b
    ```
3.  **Start Server**:
    ```bash
    ollama serve
    ```
4.  **Configure Environment**:
    Ensure your `.env` file has the Gateway configuration (see `.env.example`):
    ```env
    OLLAMA_BASE_URL=http://127.0.0.1:11434
    OLLAMA_WORKER_MODEL=llama3.1:8b
    OLLAMA_STRATEGIST_MODEL=qwen2.5:14b
    LLM_MAX_CONCURRENCY=2
    ```

## Usage

### Direct Usage (Gateway)

```python
from backend.llm import LLMGateway

# Chat (Preferred)
response = await LLMGateway.chat(
    messages=[{"role": "user", "content": "Analyze revenue trends."}],
    agent_id="akasha",  # Routes to Strategist Model
    temperature=0.5
)

if response.ok:
    print(response.content)

# Generate (Completion)
response = await LLMGateway.generate(
    prompt="Write a sales email.",
    agent_id="webscraper", # Routes to Worker Model
)
```

## Testing

Run the included test script to verify connection and routing:

```bash
python -m backend.llm.test_gateway
```
