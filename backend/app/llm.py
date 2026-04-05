import functools
import logging
import os
import time
from typing import TypeVar, Type
from openai import AzureOpenAI
from pydantic import BaseModel

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


@functools.cache
def _get_client() -> tuple[AzureOpenAI, str]:
    """Initialised once on first call; cached forever after."""
    missing = [
        v for v in (
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_API_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT",
        )
        if not os.environ.get(v)
    ]
    if missing:
        raise RuntimeError(
            f"Cannot initialise Azure OpenAI client — missing env vars: {missing}"
        )
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_API_ENDPOINT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]
    log.info("Azure OpenAI client initialised  deployment=%s", deployment)
    return client, deployment


def chat_json(prompt: str, system: str, response_model: Type[T]) -> T:
    client, deployment = _get_client()
    log.info("LLM call  deployment=%s  response_model=%s", deployment, response_model.__name__)
    t0 = time.perf_counter()
    response = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        response_format=response_model,
    )
    elapsed = time.perf_counter() - t0
    usage = response.usage
    log.info(
        "LLM done  elapsed=%.2fs  prompt_tokens=%s  completion_tokens=%s",
        elapsed,
        usage.prompt_tokens if usage else "?",
        usage.completion_tokens if usage else "?",
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise ValueError(
            f"LLM returned no structured output for {response_model.__name__} "
            f"(possible refusal: {response.choices[0].message.refusal!r})"
        )
    return parsed
