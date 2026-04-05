# Thought Boxes – Creative Meeting Canvas

## Project Overview

Thought Boxes is a locally-executed, Docker-based application that transforms raw client meeting transcripts into structured creative springboards. It runs as a containerised service, connects to a local language model (Ollama, running as a docker service, initial focus), or Azure OpenAi for all language processing, and performs live web research to contextualise findings before generating a set of creative directions.

This document is the ground-truth reference for the project. Use it to generate solution outlines, architecture proposals, and implementation plans.

---

## Constraints & Decisions

| Attribute | Decision |
|---|---|
| Execution | Local Docker container — no cloud hosting |
| LLM Provider | local model, may be swapped to Azure Open AI later |
| Web Research | Live web search API (Bing Search API or Serper) called at runtime |
| Input | Static transcript file uploaded via the tool |
| DNA Configuration | file mounted into the container, editable by the team with the agencies creative method defined |
| Steering Input | User-provided guidance entered in the UI before processing begins |
| Output | Structured data returned from the backend; presentation layer TBD |
| Export | PDF and/or plain text export of full output |

---

## Current Focus

**Backend only.** The frontend will be React (Vite) but is out of scope for now. All solution proposals should focus on the Python/FastAPI orchestration layer, pipeline stages, Docker setup, and API contracts. Frontend integration points should be defined as clean API boundaries only.

---

## System Architecture

The application runs as a multi-service Docker Compose stack on a local machine.

| Service | Technology | Responsibility |
|---|---|---|
| API / Orchestrator | Python (FastAPI) | Receives requests, orchestrates the 3-stage pipeline, calls AI service and the search API, returns structured JSON |
| Frontend (later) | React + Vite | Out of scope for now — define API contracts only - create dummy frontend only, upload then return into markdown text box |
| DNA Config | YAML file (host volume mount) | Loaded at container start; hot-reloadable without restart |
| Session Store | Local filesystem (JSON files) | Each run saved as a timestamped file for reference and replay |

---

## Core Components

The backend is composed of seven discrete building blocks. Each should be developed and tested independently, then wired together through the FastAPI orchestration layer.

### A — Thought Boxes DNA Engine
The agency's strategic frameworks, question hierarchies, and creative principles encoded as a structured YAML configuration file.

- YAML schema with named pillars, sub-questions, and weighting hints
- Loaded at container start; hot-reloadable without restart
- Acts as the system prompt layer injected into every LLM call
- Version-controlled alongside the codebase

If this is not provided, placeholder an ideal local data model and dummy creative agency directions.

**YAML sections:**

| Section | Purpose |
|---|---|
| `agency_identity` | One-paragraph description of TB's philosophy and strategic approach |
| `pillars` | Named strategic pillars (e.g. Tension Finder, Springboard Moment), each with guiding questions |
| `output_principles` | Rules for tone, length, avoid-list, preferred framing |
| `example_directions` | 2–3 anonymised example creative directions to calibrate output style |
| `search_guidance` | What kinds of sources and topics TB typically finds useful in research |

---

### B — Transcript Ingestor
Accepts a raw transcript file and prepares it for AI processing.

- Accepts `.txt` as upload or pasted text
- Pre-processing pass to strip filler, timestamps, and low-signal content
- Chunking strategy for long transcripts
- Relevancy checks and filtering to surface key information
- Returns a cleaned, structured transcript object for downstream stages
    Use pdyantic in the backend (python.)

---

### C — Steering Input Layer
Captures user intent before the main processing pipeline runs, shaping all downstream outputs.

- Free-text field for directional notes (e.g. `'focus on sustainability angle'`)
- All inputs bundled into a single `steering_payload` JSON object, appended to the DNA context for all LLM calls

---

### D — DNA-Driven Structuring (Stage 1)
Applies the Thought Boxes DNA to the cleaned transcript to produce a structured strategic brief.

- LLM call: `transcript + DNA YAML + steering_payload → structured output`
- Extracts: core problem, client signals, opportunities, tensions
- **Consideration:** output should be a knowledge graph or semi-templated structure rather than raw LLM string output — the transcript is mapped onto a graph informed by the TB DNA
    Initially Pydantic object, knowledge graph may come later?
- Output schema defined upfront so the API contract is stable
- Brief stored in session state for use by Stages 2 and 3

---

### E — AI-Accelerated Research (Stage 2)
Uses the structured brief to generate targeted web searches, retrieve results, and synthesise findings.

- LLM generates 4–6 focused search queries from the brief, each targeting a different angle: market context, competitor positioning, cultural signals, sector trends
- Queries fired against live search API (Bing Search API preferred; Serper as alternative)
- Top 5 results retrieved per query; low-quality domains filtered via configurable blocklist
- Full text fetched for top 2–3 results per query
- Results cached within the session to avoid repeated API calls on re-runs
- Second LLM call synthesises findings into a ~400–600 word research summary structured as: market context, relevant signals, creative seeds
- Source URLs preserved and returned in the response payload

---

### F — Creative Direction Generator (Stage 3)
Synthesises the brief and research into a set of distinct creative directions.

- LLM call: `brief + research summary + DNA + steering_payload → 3–5 directions`
- Each direction contains: title, one-line concept, rationale, connection to brief
- Output as structured JSON
- Directions ranked by alignment to stated brief priorities

---

### G — Session & Export Layer
Manages session persistence and export. (Presentation rendering is out of scope for now.)

- Each completed run saved as a timestamped JSON file to the local filesystem
- Export to PDF and/or plain text
- API endpoints expose session data for retrieval and replay

---

## End-to-End Processing Flow

User uploads transcript
→ API receives raw text. No processing begins until confirmed.
Transcript pre-processing (Component B)
→ Clean, chunk, and score transcript. Store in session state.
Steering input collected (Component C)
→ Bundle quote selections, directional notes, exclusions, and pillar focus
into a steering_payload JSON object.
Stage 1 — DNA-Driven Structuring (Component D)
→ LLM call: transcript + DNA YAML + steering_payload
→ Output: structured graph/brief (problem, signals, opportunities, tensions)
Stage 2a — Research query generation (Component E)
→ LLM call: structured brief → 4–6 targeted search queries
Stage 2b — Live web research (Component E)
→ Queries fired against search API
→ Results filtered, top sources fetched in full
Stage 2c — Research synthesis (Component E)
→ LLM call: retrieved content → research summary with source attribution
Stage 3 — Creative direction generation (Component F)
→ LLM call: brief + research summary + DNA + steering_payload
→ Output: 3–5 structured creative directions as JSON
Session saved (Component G)
→ Full output written to timestamped JSON file
→ API response returned to client

---

## API Contract (Frontend Boundary)

The following endpoints should be defined. These are the only integration points the frontend (React/Vite) will consume — keep them stable and well-documented.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/session/upload` | Upload a transcript file, receive a session ID |
| `POST` | `/session/{id}/steer` | Submit the steering payload |
| `POST` | `/session/{id}/run` | Trigger the full 3-stage pipeline |
| `GET` | `/session/{id}/status` | Poll processing status per stage |
| `GET` | `/session/{id}/output` | Retrieve full structured output (brief, research, directions) |
| `GET` | `/session/{id}/export` | Download PDF or plain text export |

Streaming support (where Azure OpenAI supports it) should be available via SSE on the `/run` endpoint.

---

## Loading & Progress States (API-Level)

The backend should emit stage-level progress events so the frontend can display meaningful feedback. Define these as part of the SSE or polling contract:

- **Stage 1:** `reading_transcript` → `applying_dna` → `building_brief`
- **Stage 2:** `generating_queries` → `running_searches` → `synthesising_research`
- **Stage 3:** `generating_directions` → `complete`

---

## Development Priorities

1. Docker Compose stack with FastAPI service and YAML volume mount
2. DNA Engine — YAML loader and system prompt builder
3. Transcript Ingestor — cleaning, chunking, and session state
4. Stage 1 — DNA-Driven Structuring with defined output schema
5. Stage 2 — Research pipeline (query generation → search → synthesis)
6. Stage 3 — Creative direction generation
7. Session persistence and export
8. API contract finalisation for frontend handoff