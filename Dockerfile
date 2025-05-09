FROM ghcr.io/astral-sh/uv:python3.11-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

WORKDIR /hyperion

COPY requirements-common.txt .
COPY requirements-prod.txt .
RUN uv pip install --system --no-cache-dir -r requirements-prod.txt

COPY init.py .
COPY alembic.ini .
COPY assets assets/
COPY app app/

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000

ENTRYPOINT ["./start.sh"]
