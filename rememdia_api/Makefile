.PHONY: run tui

run:
	uv run fastapi dev api/api.py

tui:
	uv run cli/tui.py

test:
	REM_ENV=test uv run pytest -vv
