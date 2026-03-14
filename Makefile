init:
	uv sync

lint:
	uv format

format:
	uv run ruff format .

analyze:
	uv run ruff check

fix:
	uv run ruff check --fix

types:
	uv run ty check
