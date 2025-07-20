from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
import threading
import time

app = FastAPI()

jobs: Dict[str, dict] = {}

class ScheduleRequest(BaseModel):
    task: str

@app.post("/schedule")
def schedule_job(req: ScheduleRequest):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "pending", "result": None}
    # In production, launch a new agent Docker container here for isolation
    def run_job():
        jobs[job_id]["status"] = "running"
        time.sleep(5)  # Simulate work
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result"] = f"/downloads/{job_id}.zip"
    threading.Thread(target=run_job, daemon=True).start()
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resp = {"status": job["status"]}
    if job["status"] == "complete":
        resp["download_url"] = job["result"]
    return resp 