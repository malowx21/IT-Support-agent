FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY --chown=app:app agent ./agent
COPY --chown=app:app api ./api
COPY --chown=app:app mcp_server ./mcp_server
COPY --chown=app:app rag ./rag
COPY --chown=app:app config.py ./config.py

RUN mkdir -p /app/data \
    && chown -R app:app /app


FROM base AS test

COPY --chown=app:app tests ./tests
COPY --chown=app:app pyproject.toml ./pyproject.toml

USER app

CMD ["pytest", "-q"]


FROM base AS production

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
