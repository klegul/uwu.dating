FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY . .
RUN uv sync --no-dev --locked --no-editable

RUN chmod -R o=rx /app

EXPOSE 9090

CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:9090", "wsgi:app"]
