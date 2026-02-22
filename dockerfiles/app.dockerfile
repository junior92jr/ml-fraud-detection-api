ARG VARIANT=3.11
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN if [ "$USER_GID" != "1000" ] || [ "$USER_UID" != "1000" ]; then \
    groupmod --gid $USER_GID vscode && usermod --uid $USER_UID --gid $USER_GID vscode; \
    fi

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional gcc build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip==24.0 setuptools==69.0.3 wheel==0.43.0 uv

COPY --chown=vscode:vscode pyproject.toml uv.lock /workspace/

WORKDIR /workspace
COPY --chown=vscode:vscode . /workspace

RUN uv venv /workspace/.venv && \
    uv sync --python /workspace/.venv/bin/python

ENV PATH="/workspace/.venv/bin:$PATH"
