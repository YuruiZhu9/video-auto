# OpenClaw Cross-Device Control — Dockerfile
FROM python:3.11-slim

LABEL maintainer="OpenClaw User"
LABEL description="OpenClaw Cross-Device Control (clawctl)"

# ── 依赖 ────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY code/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ── 应用代码 ─────────────────────────────────────────────────────────────────
COPY code/ /app/

# ── 入口 ─────────────────────────────────────────────────────────────────────
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:8080/api/v1/health || exit 1

CMD ["python", "server.py"]
