# Job Market Intelligence Platform

An end-to-end portfolio project that turns job-posting data into actionable labor-market intelligence.

## What it does

- Executive dashboard for job volume, salary, experience, and hiring trends
- Role and location intelligence
- Skill-demand analysis and skill co-occurrence
- Job search and filtering
- Personal skill-gap analyzer
- Recommended next skills based on target role demand
- CSV ingestion pipeline for replacing demo data with real/public job data
- Optional Adzuna API ingestion (requires your own free API credentials)
- SQLite analytics store for a zero-cost local setup
- Dockerized deployment

> The bundled dataset is **synthetic demo data** generated for the project. It is intentionally labeled as synthetic so the portfolio never presents fabricated market statistics as real-world facts.

## Architecture

```text
CSV / JSON / Optional API
          |
          v
   Ingestion + Cleaning
          |
          v
       SQLite
          |
          +----------------------+
          |                      |
          v                      v
     Analytics Engine       Skill Gap Engine
          |                      |
          +----------+-----------+
                     |
                     v
              Streamlit UI
                     |
            CSV / insights export
```

## Tech stack

Python, Pandas, SQLite, Streamlit, Plotly, scikit-learn, Requests, Docker.

## Run locally

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the demo dataset and database

```bash
python scripts/generate_demo_data.py
python scripts/ingest_jobs.py --input data/jobs.csv
```

### 4. Start the app

```bash
streamlit run app/main.py
```

Open `http://localhost:8501`.

## Optional: pull public job data from Adzuna

Set your credentials as environment variables:

```bash
set ADZUNA_APP_ID=your_app_id
set ADZUNA_APP_KEY=your_app_key
```

or on macOS/Linux:

```bash
export ADZUNA_APP_ID=your_app_id
export ADZUNA_APP_KEY=your_app_key
```

Then:

```bash
python scripts/fetch_adzuna.py --country in --what "data analyst" --where "India" --pages 3
python scripts/ingest_jobs.py --input data/adzuna_jobs.csv
```

The adapter is deliberately separated from the analytics layer so the rest of the product works even without an external API.

## Project highlights for your resume

**Job Market Intelligence Platform**  
Built an end-to-end labor-market analytics platform using Python, SQL/SQLite, Pandas, Plotly, and Streamlit; developed ingestion, salary/location analytics, skill co-occurrence analysis, and a personalized skill-gap recommendation engine, with Dockerized deployment and optional external job-data ingestion.

## Suggested portfolio story

1. Start with the executive dashboard.
2. Explain the difference between *job volume* and *skill demand*.
3. Show a target role, e.g. Data Analyst, and compare the top requested skills.
4. Paste a sample resume or enter your current skills.
5. Demonstrate the skill gap and ranked learning priorities.
6. Explain how the same analytics layer can be fed with real job data through the ingestion adapter.

## Notes

- Never claim the included numbers are real market statistics.
- For production use, use a source/API whose terms permit your intended use.
- The recommendation engine is heuristic and should be presented as decision support, not a hiring predictor.
