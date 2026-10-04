import pandas as pd

from app.analytics import extract_skills, skill_gap


def test_extract_skills():
    result = extract_skills("I use Python, Power BI and PostgreSQL", ["Python", "Power BI", "PostgreSQL"])
    assert set(result) == {"Python", "Power BI", "PostgreSQL"}


def test_skill_gap():
    jobs = pd.DataFrame({
        "job_id": ["1", "2", "3"],
        "title": ["Data Analyst", "Data Analyst", "Engineer"],
    })
    skills = pd.DataFrame({
        "job_id": ["1", "1", "2", "2", "3"],
        "skill": ["SQL", "Excel", "SQL", "Python", "Docker"],
    })
    out = skill_gap(jobs, skills, "Data Analyst", ["SQL"])
    row = out[out["skill"] == "Python"].iloc[0]
    assert bool(row["has_skill"]) is False
    assert row["demand_share"] == 0.5
