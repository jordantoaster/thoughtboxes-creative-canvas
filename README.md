# Thought Boxes — Creative Canvas

Transforms meeting transcripts into structured creative directions using Azure OpenAI.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — only hard dependency
- A `.env` file at the project root with Azure OpenAI credentials (see `.env`)

## Run

```bash
docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Usage

1. Open http://localhost:5173
2. Upload a `.txt` meeting transcript
3. Optionally add steering notes (e.g. _"focus on sustainability angle"_)
4. Click **Run** — the pipeline generates a strategic brief and 3 creative directions