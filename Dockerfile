FROM python:3.11.4-slim as base

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

FROM base as builder

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM base as test

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

RUN apt-get update \
  && apt-get -y install tesseract-ocr

COPY monopoly ./monopoly
COPY tests ./tests
RUN poetry install

CMD ["python", "-m", "poetry", "run", "task", "test"]

FROM base as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

RUN apt-get update \
  && apt-get -y install tesseract-ocr

COPY monopoly ./monopoly

CMD ["python", "-m", "monopoly.main"]
