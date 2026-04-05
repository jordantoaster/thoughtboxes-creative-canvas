"""
Stage 3 — Creative Direction Generator — Component F.

Takes the structured brief and steering payload, calls the LLM with the
DNA system prompt, and returns a list of CreativeDirection objects.
"""

import logging
from app.models import (
    StructuredBrief,
    SteeringPayload,
    ResearchResult,
    CreativeDirection,
    CreativeDirectionList,
)
from app import llm
from app.pipeline.dna import build_system_prompt

log = logging.getLogger(__name__)


def generate_directions(
    brief: StructuredBrief,
    research: list[ResearchResult],
    steering: SteeringPayload,
) -> list[CreativeDirection]:
    research_section = (
        "\n\nResearch context: (no external research in this run)"
        if not research
        else "\n\nResearch context:\n"
        + "\n".join(
            f"- {r.query}: {r.results[:2]}" for r in research
        )
    )

    steering_section = (
        f"\n\nSteering notes: {steering.steering_notes}"
        if steering.steering_notes.strip()
        else ""
    )

    brief_text = f"""Core problem: {brief.core_problem}

Client signals:
{chr(10).join(f'- {s}' for s in brief.client_signals)}

Opportunities:
{chr(10).join(f'- {o}' for o in brief.opportunities)}

Tensions:
{chr(10).join(f'- {t}' for t in brief.tensions)}"""

    prompt = f"""Generate 3 distinct creative directions based on the strategic brief below.

STRATEGIC BRIEF:
{brief_text}{research_section}{steering_section}

Each direction must be genuinely distinct — not variations on the same idea.
Apply the Thought Boxes strategic pillars. Be sharp and specific.

Return a JSON object with a single key "directions" containing an array of 3 objects,
each with: title, concept, rationale, connection_to_brief."""

    log.info(
        "Director  signals=%d  opportunities=%d  tensions=%d  research_results=%d",
        len(brief.client_signals),
        len(brief.opportunities),
        len(brief.tensions),
        len(research),
    )
    result = llm.chat_json(
        prompt=prompt,
        system=build_system_prompt(),
        response_model=CreativeDirectionList,
    )
    directions = result.directions
    log.info(
        "Director done  directions=%d  titles=%s",
        len(directions),
        [d.title for d in directions],
    )
    return directions
