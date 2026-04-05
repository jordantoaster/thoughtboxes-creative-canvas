"""
Formatter — converts PipelineOutput to a clean markdown string for the frontend.
"""

import logging
from app.models import PipelineOutput

log = logging.getLogger(__name__)


def to_markdown(output: PipelineOutput) -> str:
    lines: list[str] = []

    lines.append("# Thought Boxes — Creative Canvas\n")

    # --- Strategic Brief ---
    lines.append("## Strategic Brief\n")
    lines.append(f"**Core Problem**\n\n{output.brief.core_problem}\n")

    lines.append("**Client Signals**\n")
    for signal in output.brief.client_signals:
        lines.append(f"- {signal}")
    lines.append("")

    lines.append("**Opportunities**\n")
    for opp in output.brief.opportunities:
        lines.append(f"- {opp}")
    lines.append("")

    lines.append("**Tensions**\n")
    for tension in output.brief.tensions:
        lines.append(f"- {tension}")
    lines.append("")

    # --- Research ---
    lines.append("## Research\n")
    if not output.research:
        lines.append("*Web research not run in this session.*\n")
    else:
        for r in output.research:
            lines.append(f"### {r.query}")
            for result in r.results:
                lines.append(f"- {result}")
            lines.append("")

    # --- Creative Directions ---
    lines.append("## Creative Directions\n")
    for i, direction in enumerate(output.directions, start=1):
        lines.append(f"### {i}. {direction.title}\n")
        lines.append(f"**Concept:** {direction.concept}\n")
        lines.append(f"**Rationale:** {direction.rationale}\n")
        lines.append(f"**Connection to brief:** {direction.connection_to_brief}\n")

    markdown = "\n".join(lines)
    log.info(
        "Formatter done  session=%s  output_chars=%d  output_lines=%d",
        output.session_id,
        len(markdown),
        markdown.count("\n"),
    )
    return markdown
