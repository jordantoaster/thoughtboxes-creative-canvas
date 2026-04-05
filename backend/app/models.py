from pydantic import BaseModel


class CleanedTranscript(BaseModel):
    session_id: str
    raw_text: str
    cleaned_text: str
    chunks: list[str]


class SteeringPayload(BaseModel):
    steering_notes: str = ""


class StructuredBrief(BaseModel):
    core_problem: str
    client_signals: list[str]
    opportunities: list[str]
    tensions: list[str]


class ResearchResult(BaseModel):
    query: str
    results: list[dict]


class CreativeDirection(BaseModel):
    title: str
    concept: str
    rationale: str
    connection_to_brief: str


class CreativeDirectionList(BaseModel):
    """Wrapper so Ollama can return a top-level object containing the list."""
    directions: list[CreativeDirection]


class PipelineOutput(BaseModel):
    session_id: str
    transcript: CleanedTranscript
    brief: StructuredBrief
    research: list[ResearchResult]
    directions: list[CreativeDirection]


class UploadResponse(BaseModel):
    session_id: str


class RunRequest(BaseModel):
    steering_notes: str = ""


class RunResponse(BaseModel):
    session_id: str
    markdown: str
