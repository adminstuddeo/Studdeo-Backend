FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /backend

COPY pyproject.toml  uv.lock ./

COPY app ./app

RUN uv sync --frozen

EXPOSE 8000

ENTRYPOINT ["uv", "run", "uvicorn", "app.main:app" ,"--port", "8000", "--host", "0.0.0.0"]
