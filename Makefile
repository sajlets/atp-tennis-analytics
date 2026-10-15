.PHONY: setup download load test all

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

download:
	.venv/bin/python src/download.py

load:
	.venv/bin/python src/load.py

test:
	.venv/bin/python -m pytest

all: download load