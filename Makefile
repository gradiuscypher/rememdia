.PHONY: run tui

run:
	uv run fastapi dev api/api.py

tui:
	uv run cli/tui.py
