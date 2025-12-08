# AI REVENUE COMMAND CENTER - DOCKERFILE
# Production-ready container for real-world operations

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    BUSINESS_DB_PATH="/data/business_database.db" \
    AUDIT_LOG_DB="/data/audit_log.db" \
    VECTOR_MEMORY_DB="/data/vector_memory.db" \
    APPROVAL_QUEUE_DB="/data/approval_queue.db" \
    WORKFLOW_SCHEDULER_DB="/data/workflow_scheduler.db" \
    CREDENTIAL_VAULT_DB="/data/credential_vault.db"

# Set work directory
WORKDIR /app

# Create data directory for persistent database storage
RUN mkdir -p /data /app/logs && \
    chown -R 1000:1000 /data /app/logs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser && \
    chown -R appuser:appuser /app /data
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Command to run the application
# Command to run the application
CMD ["gunicorn", "backend.main_server:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]

