FROM harbor.aiby.tools/dockerhub/python:3.11-bookworm AS builder

ARG POETRY_VERSION=1.8.2
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app


RUN python -m venv /poetry-venv \
  && /poetry-venv/bin/pip install --no-cache-dir "poetry==${POETRY_VERSION}" "poetry-plugin-export==1.8.0"

COPY ./pyproject.toml ./poetry.lock* /app/
COPY ./alembic.ini /app
COPY ./alembic /app/alembic

RUN /poetry-venv/bin/poetry config warnings.export false \
  && /poetry-venv/bin/poetry export -f requirements.txt --output requirements.txt --without-hashes \
  && python -m pip install --upgrade --no-cache-dir pip setuptools wheel \
  && python -m pip install --no-cache-dir --ignore-installed --no-compile --prefer-binary --only-binary=:all: -r requirements.txt --target /opt/site-packages --upgrade \
  && find /opt/site-packages -type d \( -name tests -o -name __pycache__ \) -prune -exec rm -rf {} + \
  && find /opt/site-packages -type f -name "*.pyc" -delete \
  && rm -rf /root/.cache/pip

COPY ./src /app/src


FROM harbor.aiby.tools/gcr.io/distroless/python3-debian12:nonroot AS runtime

LABEL org.opencontainers.image.title="mh" \
      org.opencontainers.image.description="Core-сервис Mental Health" \
      org.opencontainers.image.url="https://git.aiby.tools/mental-ai/mental-ai-server/mh" \
      org.opencontainers.image.source="https://git.aiby.tools/mental-ai/mental-ai-server/mh.git"

WORKDIR /app

COPY --from=builder /opt/site-packages /opt/site-packages
COPY --from=builder /app/src /app/src
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/alembic /app/alembic

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/opt/site-packages:/app/src" \
    PYTHONOPTIMIZE=2

EXPOSE 8000

ENTRYPOINT [ \
    "/usr/bin/python3", \
    "-m", "gunicorn", \
    "--workers", "1", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--bind", "0.0.0.0:8000", \
    "--worker-connections", "1000", \
    "run:app" \
]
