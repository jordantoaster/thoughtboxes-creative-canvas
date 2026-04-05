"""
API routes — session upload and run endpoints.
Session state is held in a simple in-memory dict (sufficient for local, single-user use).
"""

import logging
import time
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models import (
    UploadResponse,
    RunRequest,
    RunResponse,
    PipelineOutput,
    SteeringPayload,
)
from app.pipeline import ingestor, structurer, researcher, director, formatter

log = logging.getLogger(__name__)
router = APIRouter()

# In-memory session store: session_id -> PipelineOutput (once run) or CleanedTranscript (before run)
_sessions: dict = {}


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/session/upload", response_model=UploadResponse)
async def upload_transcript(file: UploadFile = File(...)) -> UploadResponse:
    try:
        if file.content_type not in ("text/plain",) and not (
            file.filename or ""
        ).endswith(".txt"):
            raise HTTPException(
                status_code=415,
                detail="Only plain text (.txt) files are supported.",
            )

        raw_bytes = await file.read()
        try:
            raw_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text.")

        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        session_id = str(uuid.uuid4())
        cleaned = ingestor.ingest(session_id=session_id, raw_text=raw_text)
        _sessions[session_id] = {"transcript": cleaned, "output": None}
        log.info("Upload  session=%s  chars=%d  chunks=%d", session_id, len(raw_text), len(cleaned.chunks))

        return UploadResponse(session_id=session_id)

    except HTTPException:
        raise
    except Exception:
        log.exception("Upload failed unexpectedly")
        raise HTTPException(status_code=500, detail="Upload error — check backend logs.")


@router.post("/session/{session_id}/run", response_model=RunResponse)
def run_pipeline(session_id: str, body: RunRequest) -> RunResponse:
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        transcript = session["transcript"]
        steering = SteeringPayload(steering_notes=body.steering_notes)
        t_start = time.perf_counter()
        log.info("Pipeline start  session=%s  steering=%r", session_id, steering.steering_notes or "(none)")

        # Stage 1 — Structuring
        log.info("Stage 1/3 — structuring brief")
        brief = structurer.structure(transcript=transcript, steering=steering)
        log.info("Stage 1/3 done  problem=%r", brief.core_problem[:80])

        # Stage 2 — Research (stub, returns [])
        log.info("Stage 2/3 — research (stub)")
        research_results = researcher.research(brief=brief)
        log.info("Stage 2/3 done  results=%d", len(research_results))

        # Stage 3 — Creative Directions
        log.info("Stage 3/3 — generating creative directions")
        directions = director.generate_directions(
            brief=brief,
            research=research_results,
            steering=steering,
        )
        log.info("Stage 3/3 done  directions=%d", len(directions))

        elapsed = time.perf_counter() - t_start
        log.info("Pipeline complete  session=%s  elapsed=%.2fs", session_id, elapsed)

        output = PipelineOutput(
            session_id=session_id,
            transcript=transcript,
            brief=brief,
            research=research_results,
            directions=directions,
        )
        _sessions[session_id]["output"] = output

        markdown = formatter.to_markdown(output)
        return RunResponse(session_id=session_id, markdown=markdown)

    except HTTPException:
        raise
    except Exception:
        log.exception("Pipeline failed  session=%s", session_id)
        raise HTTPException(status_code=500, detail="Pipeline error — check backend logs.")


@router.get("/session/{session_id}/output", response_model=PipelineOutput)
def get_output(session_id: str) -> PipelineOutput:
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session["output"] is None:
        raise HTTPException(status_code=425, detail="Pipeline has not been run yet.")
    return session["output"]
