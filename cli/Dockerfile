FROM python:3.12

RUN pip install uv

WORKDIR /tui

COPY . .
RUN uv venv
RUN uv sync

CMD ["uv", "run", "tui.py"]
