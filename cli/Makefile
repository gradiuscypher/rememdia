.PHONY: tui

tui:
	uv run tui.py
console:
	uv run textual console -x EVENT
dev:
	uv run textual run --dev tui.py
build:
	docker build -t rememdia-tui .
drun:
	docker run -it --name rememdia-tui --rm rememdia-tui
