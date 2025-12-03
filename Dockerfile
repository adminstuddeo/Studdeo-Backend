FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

COPY pyproject.toml  uv.lock ./

COPY app ./app

RUN uv sync --frozen

ENTRYPOINT ["uv", "run", "uvicorn", "app.main:main" ,"--port", "8000"]
