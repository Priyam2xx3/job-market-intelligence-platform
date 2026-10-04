.PHONY: setup data ingest run test clean

setup:
	python -m pip install -r requirements.txt

data:
	python scripts/generate_demo_data.py
	python scripts/ingest_jobs.py --input data/jobs.csv

ingest:
	python scripts/ingest_jobs.py --input data/jobs.csv

run:
	streamlit run app/main.py

test:
	python -m pytest -q

clean:
	rm -f data/jobs.db data/jobs.csv data/adzuna_jobs.csv
