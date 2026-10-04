from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import get_connection, init_db


def ingest(path: Path) -> None:
    init_db()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"job_id", "title", "company", "location", "country", "remote_type", "experience_min", "experience_max", "salary_min", "salary_max", "currency", "posted_date", "source", "url", "description", "skills"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        with get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            for row in reader:
                conn.execute(
                    """INSERT INTO jobs(job_id,title,company,location,country,remote_type,experience_min,experience_max,salary_min,salary_max,currency,posted_date,source,url,description)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(job_id) DO UPDATE SET title=excluded.title, company=excluded.company, location=excluded.location,
                       country=excluded.country, remote_type=excluded.remote_type, experience_min=excluded.experience_min,
                       experience_max=excluded.experience_max, salary_min=excluded.salary_min, salary_max=excluded.salary_max,
                       currency=excluded.currency, posted_date=excluded.posted_date, source=excluded.source, url=excluded.url, description=excluded.description""",
                    (
                        row["job_id"], row["title"], row["company"], row["location"], row["country"], row["remote_type"],
                        float(row["experience_min"] or 0), float(row["experience_max"] or 0),
                        float(row["salary_min"] or 0), float(row["salary_max"] or 0), row["currency"], row["posted_date"],
                        row["source"], row["url"], row["description"],
                    ),
                )
                conn.execute("DELETE FROM job_skills WHERE job_id=?", (row["job_id"],))
                for skill in filter(None, [s.strip() for s in row["skills"].split(";")]):
                    conn.execute("INSERT OR IGNORE INTO job_skills(job_id, skill) VALUES (?, ?)", (row["job_id"], skill))
            conn.commit()
    print(f"Ingested {sum(1 for _ in csv.DictReader(path.open('r', encoding='utf-8-sig'))):,} rows from {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a job CSV into the analytics database.")
    parser.add_argument("--input", required=True, help="CSV file to ingest")
    args = parser.parse_args()
    ingest(Path(args.input))
