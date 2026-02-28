init:
	uv sync

lint:
	uv format

analyze:
	uv run ruff check

types:
	uv run ty check
