.PHONY: install dev test lint example clean

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev,examples]"

test:
	pytest -q

lint:
	ruff check .

example:
	python examples/example_basic.py

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache outputs
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
