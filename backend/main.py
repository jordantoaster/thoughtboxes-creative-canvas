import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger(__name__)

_REQUIRED = ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_API_ENDPOINT", "AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_DEPLOYMENT")
_missing = [v for v in _REQUIRED if not os.environ.get(v)]
if _missing:
    log.error("Missing required env vars: %s — requests will fail", _missing)
else:
    log.info(
        "Azure OpenAI config OK  deployment=%s  endpoint=%s",
        os.environ["AZURE_OPENAI_DEPLOYMENT"],
        os.environ["AZURE_OPENAI_API_ENDPOINT"],
    )

app = FastAPI(title="Thought Boxes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
