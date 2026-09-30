# Optional fallback only when real Docker isolation is available.
FROM python:3.13-slim
RUN useradd --uid 1000 --create-home worker
USER worker
WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# docker build -t artemis-worker:local -f engines/execution/Dockerfile .
# The host enforces network:none, read-only root, dropped capabilities and quotas.
