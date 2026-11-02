.PHONY: install data run test lint all

install:
	pip install -r requirements-dev.txt
	pip install -e .

data:
	python scripts/download_data.py

run: data
	python -m olist_analysis.pipeline

test:
	pytest -q

lint:
	ruff check src scripts tests

all: install run test
