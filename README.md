# AI Background Music Engine for Video

A Python-based API prototype that generates instrumental background music for video projects. It provides an asynchronous job interface and produces a WAV mix, separate instrument stems, and a JSON manifest.

> **Current status:** This is an early procedural music-generation prototype. It synthesizes audio using NumPy and SciPy; it does not yet generate music from AI prompt understanding. Features such as narration ducking, tempo/key control, and loopable output are not fully implemented.

## Features

- REST API built with FastAPI.
- Background music jobs with job IDs and status tracking.
- Configurable requested duration from 5 to 300 seconds.
- Procedurally synthesized harmony, bass, melody, and drums.
- WAV mix and individual stem files.
- JSON manifest containing output information.
- Health and readiness endpoints.
- Interactive API documentation through Swagger UI.

## Technology Stack

- Python 3.12
- FastAPI and Uvicorn
- NumPy and SciPy
- Pydantic
- Pytest and HTTPX

## Project Structure

```text
ai-background-music-engine/
├── app/
│   ├── main.py
│   ├── main_backup.py
│   └── generate_demo.py
├── outputs/
│   └── demo/
│       ├── mix.wav
│       ├── harmony.wav
│       ├── bass.wav
│       ├── melody.wav
│       ├── drums.wav
│       └── music_manifest.json
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment in PowerShell:

```powershell
python3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install fastapi "uvicorn[standard]" pydantic pytest httpx numpy scipy pretty_midi mido
```

## Run the API

From the project root, run:

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Readiness check: http://127.0.0.1:8000/ready

## Create a Music Job

Send a `POST` request to `/api/v1/music/jobs` with JSON such as:

```json
{
  "prompt": "Calm instrumental background music",
  "duration_s": 10
}
```

The API returns a job ID. Use that ID with `GET /api/v1/jobs/{job_id}` to check the job status and retrieve the output links.

Generated files are served under `/outputs/demo/`.

## Current Limitations

- Music generation is procedural, not AI-driven prompt matching.
- Prompt, tempo, key, narration, and loop settings are not yet fully applied.
- Jobs currently share an output directory, so concurrent jobs can overwrite files.
- Audio loudness, true peak, exact ending behavior, and commercial-use licensing still need formal verification.
- Docker deployment, a complete OpenAPI 3.1 specification, automated tests, and remaining assessment documentation are pending.

## Assessment Goals

The next development stages are to improve generation quality, validate audio requirements, implement missing API features, add automated tests and container support, document audio-source licensing, and prepare a reproducible demonstration.

## License

The project's overall license has not yet been finalized. See `SOURCES.md` for the licensing terms of any third-party audio assets once verified.
