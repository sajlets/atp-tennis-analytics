.PHONY: setup download load test all sql charts

charts:
	.venv/bin/python src/build_charts.py

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

sql:
	.venv/bin/python src/run_sql.py sql/01_staging.sql sql/02_quality.sql sql/03_kpis.sql