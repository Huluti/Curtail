init:
	uv sync

lint:
	uv format

analyze:
	uv run ruff check
