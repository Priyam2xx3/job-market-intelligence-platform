from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "jobs.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    country TEXT NOT NULL,
    remote_type TEXT NOT NULL,
    experience_min REAL NOT NULL,
    experience_max REAL NOT NULL,
    salary_min REAL,
    salary_max REAL,
    currency TEXT NOT NULL,
    posted_date TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id TEXT NOT NULL,
    skill TEXT NOT NULL,
    PRIMARY KEY(job_id, skill),
    FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def load_jobs() -> tuple:
    init_db()
    with get_connection() as conn:
        jobs = conn.execute("SELECT * FROM jobs ORDER BY posted_date DESC").fetchall()
        skills = conn.execute("SELECT job_id, skill FROM job_skills").fetchall()
    return jobs, skills
