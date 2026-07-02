# DealProof backend image — serves the FastAPI API and, via a different
# `command:` in docker-compose.yml, the Celery worker. Same image, two roles.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps: build tools for any compiled wheels (e.g. psycopg), plus
# libraries WeasyPrint needs to render PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        shared-mime-info \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

# `pip install .` needs the full source tree present (pyproject.toml has no
# separate [build-system]/package list, so setuptools discovers `app/` by
# scanning the tree) -- copy everything before installing rather than trying
# to cache a dependency-only layer off pyproject.toml alone.
COPY . .
RUN pip install .

EXPOSE 8000

# Default role: the API server. The worker service overrides `command:` in
# docker-compose.yml to run `celery -A app.pipeline.tasks worker` instead.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
