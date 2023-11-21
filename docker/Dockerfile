FROM python:3.11.6-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VERSION=1.7.1 \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="/root/.local/bin:$PATH"

# Install system dependencies:
RUN apt-get update && \
    apt-get install --no-install-recommends -y bash curl build-essential libpq-dev && \
    curl -sSL https://install.python-poetry.org | python - && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy requirements to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml  ./

# Install python dependencies
RUN poetry install --no-interaction --no-ansi

ENTRYPOINT ["python", "main.py"]
