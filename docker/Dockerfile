FROM python:3.10.7-slim-buster

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="/root/.local/bin:$PATH"

# Install system dependencies:
RUN apt-get update && \
    apt-get install --no-install-recommends -y bash curl build-essential && \
    curl -sSL https://install.python-poetry.org | python - --version 1.2.0 && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Setup permissions
RUN groupadd -r web && \
    useradd -d /code -r -g web web && \
    chown web:web -R /code

# Copy requirements to cache them in docker layer
COPY --chown=web:web ./poetry.lock ./pyproject.toml  ./

# Install python dependencies
RUN poetry export --only main --without-urls --without-hashes --output=requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Run as non-root user
USER web

# Copy application code
COPY --chown=web:web trademark_finder trademark_finder/
COPY --chown=web:web main.py ./
COPY --chown=web:web populate_db.py ./

ENTRYPOINT ["python"]
CMD ["main.py"]
