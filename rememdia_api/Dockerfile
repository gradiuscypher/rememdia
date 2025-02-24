FROM python:3.12

RUN pip install uv

WORKDIR /api

COPY . .
RUN uv venv
RUN uv sync

CMD ["uv", "run", "fastapi", "run"]
