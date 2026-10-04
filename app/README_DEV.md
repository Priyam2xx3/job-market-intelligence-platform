# Developer notes

The app intentionally separates:

- `db.py`: storage/schema
- `analytics.py`: business logic and recommendation engine
- `main.py`: UI only
- `scripts/generate_demo_data.py`: reproducible demo source
- `scripts/ingest_jobs.py`: generic ingestion contract
- `scripts/fetch_adzuna.py`: optional external source adapter

That separation is useful in interviews because you can explain how the prototype would evolve from SQLite to PostgreSQL and from a batch CSV source to scheduled ingestion.
