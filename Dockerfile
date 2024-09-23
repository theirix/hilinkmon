FROM python:3.9-slim

ENV \
  DOCKERIZE_VERSION=v0.19.0 \
	POETRY_VERSION=1.8.3 \
  POETRY_HOME="/opt/poetry" \
  PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --proto '=https' --tlsv1.3 https://github.com/powerman/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-x86_64 -o /usr/local/bin/dockerize \
    && chmod a+rx /usr/local/bin/dockerize

RUN curl -fsSL --proto '=https' --tlsv1.3 https://install.python-poetry.org | python3 -

ENV \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

ENV PATH="$POETRY_HOME/bin/:$PATH"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry install --no-dev --no-interaction --no-ansi

COPY . /app
