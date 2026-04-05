FROM python:3.13-slim

# Prevent Python from buffering stdout/stderr — ensures logs are never lost in Docker
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
RUN pip install uv --no-cache-dir

# Copy dependency manifest first for layer caching
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--no-access-log"]
