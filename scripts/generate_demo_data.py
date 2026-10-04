from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "jobs.csv"

random.seed(42)

ROLE_SKILLS = {
    "Data Analyst": ["SQL", "Excel", "Power BI", "Python", "Tableau", "Pandas", "Statistics", "Git"],
    "Business Analyst": ["SQL", "Excel", "Power BI", "Tableau", "Requirements Analysis", "Jira", "Statistics"],
    "Data Engineer": ["Python", "SQL", "PostgreSQL", "Apache Spark", "Apache Airflow", "Docker", "AWS", "Git", "Kafka"],
    "Analytics Engineer": ["SQL", "Python", "dbt", "PostgreSQL", "Git", "Power BI", "Docker", "Data Modeling"],
    "Data Scientist": ["Python", "SQL", "Machine Learning", "scikit-learn", "Pandas", "NumPy", "Statistics", "Git"],
    "ML Engineer": ["Python", "PyTorch", "TensorFlow", "Docker", "AWS", "Machine Learning", "Git", "Kubernetes"],
    "BI Developer": ["SQL", "Power BI", "DAX", "Excel", "Data Modeling", "ETL", "Git"],
    "AI Engineer": ["Python", "LLM", "RAG", "LangChain", "PyTorch", "Docker", "Git", "AWS"],
}

LOCATIONS = [
    ("Bengaluru", 1.18), ("Hyderabad", 1.08), ("Pune", 1.04), ("Chennai", 0.98),
    ("Mumbai", 1.12), ("Delhi NCR", 1.08), ("Kolkata", 0.90), ("Noida", 1.00),
    ("Gurugram", 1.10), ("Remote - India", 1.05),
]
COMPANIES = ["NovaTech", "DataForge", "CloudVista", "InsightWorks", "AsterLabs", "QuantEdge", "BlueOrbit", "Vertex Systems", "BrightScale", "Nexora"]
REMOTE_TYPES = ["Remote", "Hybrid", "On-site"]

rows = []
start = date.today() - timedelta(days=180)
for i in range(1, 1501):
    role = random.choices(list(ROLE_SKILLS), weights=[22, 16, 18, 8, 12, 8, 7, 9])[0]
    location, loc_mult = random.choice(LOCATIONS)
    company = random.choice(COMPANIES)
    exp_min = random.choice([0, 0, 1, 1, 2, 3])
    exp_max = max(exp_min + random.choice([1, 2, 3, 4]), 1)
    base = {
        "Data Analyst": 650000, "Business Analyst": 700000, "Data Engineer": 1050000,
        "Analytics Engineer": 1150000, "Data Scientist": 1000000, "ML Engineer": 1250000,
        "BI Developer": 850000, "AI Engineer": 1200000,
    }[role]
    experience_bonus = 1 + 0.08 * min(exp_max, 5)
    salary_mid = int(base * loc_mult * experience_bonus * random.uniform(0.80, 1.25))
    salary_min = int(salary_mid * random.uniform(0.82, 0.92))
    salary_max = int(salary_mid * random.uniform(1.08, 1.28))
    posted = start + timedelta(days=random.randint(0, 180))
    chosen_skills = ROLE_SKILLS[role].copy()
    # Add occasional cross-functional skills to make co-occurrence analysis realistic.
    for optional in ["Docker", "AWS", "Git", "Power BI", "SQL", "Python"]:
        if optional not in chosen_skills and random.random() < 0.18:
            chosen_skills.append(optional)
    desc = f"{role} opportunity at {company}. Work with {', '.join(chosen_skills[:5])} and collaborate with cross-functional teams."
    rows.append({
        "job_id": f"DEMO-{i:05d}", "title": role, "company": company, "location": location,
        "country": "India", "remote_type": random.choice(REMOTE_TYPES),
        "experience_min": exp_min, "experience_max": exp_max,
        "salary_min": salary_min, "salary_max": salary_max, "currency": "INR",
        "posted_date": posted.isoformat(), "source": "Synthetic Demo", "url": "",
        "description": desc, "skills": ";".join(sorted(set(chosen_skills))),
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows):,} synthetic job records at {OUT}")
