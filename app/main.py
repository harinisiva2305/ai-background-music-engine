
from pathlib import Path
from threading import Lock
from uuid import uuid4
import logging
import subprocess
import sys

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("music_engine")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
GENERATOR = PROJECT_ROOT / "app" / "generate_demo.py"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI Background Music Engine",
    version="1.0.0",
    description="API for generating procedural instrumental music demos.",
)

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_ROOT)),
    name="outputs",
)

jobs = {}
jobs_lock = Lock()


class MusicJobRequest(BaseModel):
    prompt: str = Field(min_length=1)
    duration_s: int = Field(ge=5, le=300)
    sections: list[dict] | None = None
    tempo_bpm: int | None = Field(default=None, ge=40, le=240)
    key: str | None = None
    loopable: bool = False
    narration_url: str | None = None
    seed: int | None = None
    output: str = "wav"


def process_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            return
        job["status"] = "processing"
        job["progress"] = 10
        duration = job["duration_s"]

    try:
        subprocess.run(
            [sys.executable, str(GENERATOR), str(duration)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )

        base_url = "/outputs/demo"
        result = {
            "mix_url": f"{base_url}/mix.wav",
            "stem_urls": {
                "harmony": f"{base_url}/harmony.wav",
                "bass": f"{base_url}/bass.wav",
                "melody": f"{base_url}/melody.wav",
                "drums": f"{base_url}/drums.wav",
            },
            "manifest_url": f"{base_url}/music_manifest.json",
            "note": (
                "Prototype uses procedural synthesis, not AI prompt matching. "
                "Prompt, tempo, key, narration and loop settings are not "
                "applied yet. Concurrent jobs share output files."
            ),
        }

        with jobs_lock:
            job = jobs.get(job_id)
            if job is not None:
                job["status"] = "completed"
                job["progress"] = 100
                job["result"] = result

        logger.info("Job %s completed", job_id)

    except Exception:
        logger.exception("Job %s failed", job_id)
        with jobs_lock:
            job = jobs.get(job_id)
            if job is not None:
                job["status"] = "failed"
                job["error"] = "Music generation failed. Check server logs."


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

    background_tasks.add_task(process_job, job_id)
    logger.info("Created job %s", job_id)
    return job.copy()


@app.get("/api/v1/jobs/{job_id}")
def get_music_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job.copy()
