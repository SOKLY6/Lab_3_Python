build:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv venv
	uv sync

lint:
	mypy src
	ruff format src
	ruff check --fix src

start_test:
	pytest
	pytest --cov=src test/

start:
	python3 main.py