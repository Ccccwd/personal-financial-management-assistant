# ---- Stage 1: Builder ----
FROM python:3.12-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存
COPY pyproject.toml uv.lock ./

# 使用 uv 安装依赖到虚拟环境
RUN uv sync --frozen --no-dev --no-install-project

# ---- Stage 2: Runtime ----
FROM python:3.12-slim

WORKDIR /app

# 从 builder 复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建非 root 可写目录
RUN mkdir -p /app/uploads /app/exports && chown -R appuser:appuser /app/uploads /app/exports

USER appuser

# 将 venv 加入 PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health'); exit(0)"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
