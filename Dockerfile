FROM python:3.12-slim

# install psql
RUN apt-get update
RUN apt-get -y install postgresql-client

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.0.0

RUN pip install "poetry==1.8.3"

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY wait-for-postgres.sh ./

RUN chmod +x wait-for-postgres.sh

COPY app/ app/
