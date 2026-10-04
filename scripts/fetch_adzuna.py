from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "adzuna_jobs.csv"


def clean_skills(title: str, description: str) -> list[str]:
    known = [
        "SQL", "Python", "Java", "Excel", "Power BI", "Tableau", "Pandas", "NumPy", "Statistics",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Apache Spark", "Apache Airflow", "Kafka",
        "Machine Learning", "scikit-learn", "PyTorch", "TensorFlow", "Git", "PostgreSQL", "MySQL",
        "RAG", "LLM", "LangChain", "DAX", "dbt", "Jira", "Data Modeling", "ETL",
    ]
    text = f"{title} {description}".lower()
    return sorted({s for s in known if s.lower() in text})


def fetch(country: str, what: str, where: str, pages: int) -> None:
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError("Set ADZUNA_APP_ID and ADZUNA_APP_KEY before running this script.")

    rows = []
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {"app_id": app_id, "app_key": app_key, "results_per_page": 50, "what": what, "where": where, "content-type": "application/json"}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        results = response.json().get("results", [])
        for item in results:
            title = item.get("title") or "Unknown"
            description = item.get("description") or ""
            rows.append({
                "job_id": f"ADZUNA-{item.get('id')}",
                "title": title,
                "company": (item.get("company") or {}).get("display_name", "Unknown"),
                "location": (item.get("location") or {}).get("display_name", "Unknown"),
                "country": country.upper(),
                "remote_type": "Unknown",
                "experience_min": 0,
                "experience_max": 5,
                "salary_min": item.get("salary_min") or 0,
                "salary_max": item.get("salary_max") or 0,
                "currency": "Unknown",
                "posted_date": (item.get("created") or "")[:10],
                "source": "Adzuna",
                "url": item.get("redirect_url", ""),
                "description": description.replace("\n", " "),
                "skills": ";".join(clean_skills(title, description)),
            })
        if not results:
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [
            "job_id", "title", "company", "location", "country", "remote_type", "experience_min", "experience_max",
            "salary_min", "salary_max", "currency", "posted_date", "source", "url", "description", "skills"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Fetched {len(rows):,} jobs into {OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional Adzuna job-data adapter.")
    parser.add_argument("--country", default="in")
    parser.add_argument("--what", default="data analyst")
    parser.add_argument("--where", default="India")
    parser.add_argument("--pages", type=int, default=2)
    args = parser.parse_args()
    fetch(args.country, args.what, args.where, args.pages)
