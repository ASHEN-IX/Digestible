from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tasks import scrape_and_process_link

app = FastAPI(title="Digestible API Gateway")

# Simplified Pydantic model for incoming link submission
class LinkSubmission(BaseModel):
    url: str
    user_id: str = "placeholder_user_123" # Simulating authenticated user

@app.get("/")
def read_root():
    return {"status": "Digestible API is operational"}

@app.post("/api/save-link", status_code=202) # Use 202 Accepted for async jobs
async def save_link_for_processing(submission: LinkSubmission):
    """
    Accepts a URL, immediately queues it, and returns the job ID.
    In the next phase, we will add database insertion here.
    """
    if not submission.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    # --- Key Step: Sending the Task to the Worker ---
    # We pass placeholder data (article_id) for now; in the next step, 
    # we will use the ID generated from the DB record.
    placeholder_article_id = "temp_id_1" 
    
    # .delay() is the simplest way to send a task asynchronously
    task = scrape_and_process_link.delay(placeholder_article_id, submission.url)
    
    print(f"--- API SENT JOB ---")
    print(f"Task ID: {task.id}")

    # The API returns quickly, preventing browser timeouts
    return {
        "message": "Link received and queued for processing.",
        "task_id": task.id,
        "status_check_endpoint": f"/api/status/{task.id}"
    }

@app.get("/api/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Checks the status of the job by querying the Celery backend (Redis).
    """
    task = scrape_and_process_link.AsyncResult(task_id)
    
    status_map = {
        'PENDING': 'Queued',
        'STARTED': 'Processing',
        'SUCCESS': 'Completed',
        'FAILURE': 'Failed'
    }

    return {
        "task_id": task_id,
        "status": status_map.get(task.state, task.state),
        "result": task.result if task.ready() else None
    }