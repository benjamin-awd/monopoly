FROM homebrew/brew:4.1.14 AS brew
RUN brew install john-jumbo

FROM python:3.11.4-slim AS base

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

FROM base AS builder

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM base AS test

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

RUN apt-get update \
  && apt-get -y install tesseract-ocr

COPY --from=brew /home/linuxbrew/.linuxbrew/Cellar /home/linuxbrew/.linuxbrew/Cellar
COPY --from=brew /home/linuxbrew/.linuxbrew/bin/john /home/linuxbrew/.linuxbrew/bin/john
COPY --from=brew /home/linuxbrew/.linuxbrew/lib /home/linuxbrew/.linuxbrew/lib
ENV PATH=/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH

COPY monopoly ./monopoly
COPY tests ./tests
RUN poetry install

CMD ["python", "-m", "poetry", "run", "task", "test"]

FROM base AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=brew /home/linuxbrew/.linuxbrew/Cellar /home/linuxbrew/.linuxbrew/Cellar
COPY --from=brew /home/linuxbrew/.linuxbrew/bin/john /home/linuxbrew/.linuxbrew/bin/john
COPY --from=brew /home/linuxbrew/.linuxbrew/lib /home/linuxbrew/.linuxbrew/lib
ENV PATH=/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH

RUN apt-get update \
  && apt-get -y install tesseract-ocr

COPY monopoly ./monopoly

CMD ["python", "-m", "monopoly.main"]
