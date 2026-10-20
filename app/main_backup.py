
from uuid import uuid4
from typing import Optional
from threading import Lock
from time import sleep
import logging

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("music_engine")

app = FastAPI(
    title="AI Background Music Engine",
    version="1.0.0",
    description="API for generating instrumental background music for videos.",
)

jobs = {}
jobs_lock = Lock()


class MusicJobRequest(BaseModel):
    prompt: str = Field(min_length=1)
    duration_s: int = Field(ge=5, le=300)
    sections: Optional[list[dict]] = None
    tempo_bpm: Optional[int] = Field(default=None, ge=40, le=240)
    key: Optional[str] = None
    loopable: bool = False
    narration_url: Optional[str] = None
    seed: Optional[int] = None
    output: Optional[str] = "wav"


def process_job(job_id: str):
    logger.info("Background task started for job %s", job_id)

    try:
        with jobs_lock:
            job = jobs.get(job_id)
            if job is None:
                logger.error("Job %s was not found", job_id)
                return

            job["status"] = "processing"
            job["progress"] = 10

        for progress in (30, 60, 90):
            sleep(1)

            with jobs_lock:
                job = jobs.get(job_id)
                if job is None:
                    return
                job["progress"] = progress

            logger.info(
                "Job %s progress: %s%%",
                job_id,
                progress,
            )

        with jobs_lock:
            job = jobs.get(job_id)
            if job is None:
                return

            job["status"] = "completed"
            job["progress"] = 100
            job["result"] = {
                "message": (
                    "Demo job completed successfully. "
                    "Real audio generation is not connected yet."
                )
            }

        logger.info("Job %s completed", job_id)

    except Exception:
        logger.exception("Job %s failed", job_id)

        with jobs_lock:
            job = jobs.get(job_id)
            if job is not None:
                job["status"] = "failed"
                job["error"] = "An internal error occurred."


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/api/v1/music/jobs", status_code=202)
def create_music_job(
    request: MusicJobRequest,
    background_tasks: BackgroundTasks,
):
    job_id = str(uuid4())

    job = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "prompt": request.prompt,
        "duration_s": request.duration_s,
        "result": None,
    }

    with jobs_lock:
        jobs[job_id] = job

    logger.info("Created job %s", job_id)

    background_tasks.add_task(process_job, job_id)

    return job.copy()


@app.get("/api/v1/jobs/{job_id}")
def get_music_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        return job.copy()

