"""
Stage 2 — AI-Accelerated Research — Component E (stub).

Web search is not yet implemented. Returns an empty list so the pipeline
remains complete. Slot this out for a real search implementation later.
"""

import logging
from app.models import StructuredBrief, ResearchResult

log = logging.getLogger(__name__)


def research(brief: StructuredBrief) -> list[ResearchResult]:
    """
    Stub: returns empty results.
    Future implementation: generate search queries from the brief,
    hit the search API, retrieve full text, synthesise findings.
    """
    log.info("Researcher  stub — skipping web search, returning 0 results")
    return []
