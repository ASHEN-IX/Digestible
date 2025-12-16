# app/tasks.py
from celery import Celery
import os
import time

# --- Celery Application Setup ---

# 1. Read Broker URL: The broker is Redis, specified by the environment variable
#    REDIS_URL=redis://redis:6379/0 set in docker-compose.yml
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    'digestible_tasks',
    broker=redis_url,
    backend=redis_url # Backend stores task results (optional, but useful for status)
)

# 2. Configuration: Standard settings for security and reliability
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Ensure tasks run immediately in case of a crash
    task_acks_late=True,
    # Number of times a task will be retried
    task_default_retry_limit=3,
)

# --- Task Definition ---

@app.task(bind=True, max_retries=3) # bind=True gives access to the task instance (self)
def scrape_and_process_link(self, article_id: str, url: str) -> str:
    """
    Simulated long-running task to demonstrate the async workflow.
    """
    try:
        print(f"--- WORKER RECEIVED JOB ---")
        print(f"Task ID: {self.request.id} | Processing Article ID: {article_id} for URL: {url}")

        # In a real scenario, this is where scraping, AI, and audio generation happens.
        # It must be inside a try/except block for failure handling.
        
        # Simulate work being done
        print("Simulating 5 seconds of scraping and AI processing...")
        time.sleep(5)
        
        # Simulating a successful result
        result = f"Article {article_id} processed successfully. Final status: COMPLETED."
        print(result)
        return result

    except Exception as exc:
        # --- Advanced Feature: Task Retries ---
        # If any error occurs (e.g., website scrape blocked), the task is retried.
        print(f"Task failed. Attempting retry. Error: {exc}")
        raise self.retry(exc=exc, countdown=5) # Retry in 5 seconds