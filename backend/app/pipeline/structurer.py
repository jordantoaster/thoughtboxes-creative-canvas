"""
Stage 1 — DNA-Driven Structuring — Component D.

Takes the cleaned transcript and steering payload, calls the LLM with the
DNA system prompt, and returns a structured StructuredBrief.
"""

import logging
from app.models import CleanedTranscript, SteeringPayload, StructuredBrief
from app import llm
from app.pipeline.dna import build_system_prompt

log = logging.getLogger(__name__)


def structure(transcript: CleanedTranscript, steering: SteeringPayload) -> StructuredBrief:
    # Use the first chunk(s) up to ~4000 chars so the prompt stays manageable
    log.info(
        "Structurer  session=%s  chunks=%d  steering=%r",
        transcript.session_id,
        len(transcript.chunks),
        steering.steering_notes or "(none)",
    )
    context = "\n\n---\n\n".join(transcript.chunks)[:4000]

    steering_section = (
        f"\n\nSteering notes from the team: {steering.steering_notes}"
        if steering.steering_notes.strip()
        else ""
    )

    prompt = f"""Analyse the following meeting transcript and extract a structured strategic brief.

TRANSCRIPT:
{context}{steering_section}

Return a JSON object with exactly these fields:
- core_problem: The single most important problem or challenge the client faces (1–2 sentences)
- client_signals: 3–5 direct quotes or paraphrased signals from the transcript that reveal client mindset
- opportunities: 3–5 specific opportunities identified from the transcript
- tensions: 2–4 productive tensions or contradictions that could fuel creative work"""

    log.info("Structurer  context_chars=%d  sending to LLM", len(context))
    result = llm.chat_json(
        prompt=prompt,
        system=build_system_prompt(),
        response_model=StructuredBrief,
    )
    log.info(
        "Structurer done  session=%s  signals=%d  opportunities=%d  tensions=%d",
        transcript.session_id,
        len(result.client_signals),
        len(result.opportunities),
        len(result.tensions),
    )
    return result
