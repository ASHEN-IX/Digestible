# app/tasks.py
from celery import Celery
import time

app = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

# Explicitly name the task here:
@app.task(name="app.tasks.scrape_and_process_link") 
def scrape_and_process_link(article_id, url):
    print(f"--- WORKER RECEIVED JOB ---")
    print(f"Processing Article ID: {article_id} from {url}")
    time.sleep(5)
    print(f"Article {article_id} processed successfully.")
    return True