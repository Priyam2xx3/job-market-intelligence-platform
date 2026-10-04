from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


def jobs_df(conn) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM jobs", conn)


def skills_df(conn) -> pd.DataFrame:
    return pd.read_sql_query("SELECT job_id, skill FROM job_skills", conn)


def add_salary_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["salary_mid"] = out[["salary_min", "salary_max"]].mean(axis=1)
    out["experience_mid"] = out[["experience_min", "experience_max"]].mean(axis=1)
    out["posted_date"] = pd.to_datetime(out["posted_date"], errors="coerce")
    return out


def top_skills(jobs: pd.DataFrame, skills: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    merged = skills.merge(jobs[["job_id"]], on="job_id", how="inner")
    counts = merged["skill"].value_counts().head(limit).rename_axis("skill").reset_index(name="job_count")
    if not counts.empty:
        counts["share_of_jobs"] = counts["job_count"] / max(len(jobs), 1)
    return counts


def role_summary(jobs: pd.DataFrame, query: str | None = None) -> pd.DataFrame:
    df = jobs.copy()
    if query:
        mask = df["title"].str.contains(re.escape(query), case=False, na=False)
        df = df[mask]
    return (
        df.groupby("title", as_index=False)
        .agg(job_count=("job_id", "count"), median_salary=("salary_mid", "median"), avg_experience=("experience_mid", "mean"))
        .sort_values("job_count", ascending=False)
    )


def location_summary(jobs: pd.DataFrame) -> pd.DataFrame:
    return (
        jobs.groupby("location", as_index=False)
        .agg(job_count=("job_id", "count"), median_salary=("salary_mid", "median"))
        .sort_values("job_count", ascending=False)
    )


def monthly_trend(jobs: pd.DataFrame) -> pd.DataFrame:
    trend = jobs.dropna(subset=["posted_date"]).copy()
    trend["month"] = trend["posted_date"].dt.to_period("M").astype(str)
    return trend.groupby("month", as_index=False).agg(job_count=("job_id", "count")).sort_values("month")


def skill_matrix(jobs: pd.DataFrame, skills: pd.DataFrame, target_role: str | None = None) -> pd.DataFrame:
    j = jobs
    if target_role:
        j = j[j["title"].str.contains(re.escape(target_role), case=False, na=False)]
    s = skills[skills["job_id"].isin(j["job_id"])]
    counts = s["skill"].value_counts()
    result = counts.rename_axis("skill").reset_index(name="job_count")
    result["demand_share"] = result["job_count"] / max(len(j), 1)
    return result


def cooccurrence(skills: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    if skills.empty:
        return pd.DataFrame(columns=["skill_a", "skill_b", "co_jobs"])
    common = skills["skill"].value_counts().head(limit).index.tolist()
    grouped = skills[skills["skill"].isin(common)].groupby("job_id")["skill"].apply(list)
    pairs: Counter[tuple[str, str]] = Counter()
    for job_skills in grouped:
        uniq = sorted(set(job_skills))
        for i, a in enumerate(uniq):
            for b in uniq[i + 1 :]:
                pairs[(a, b)] += 1
    rows = [{"skill_a": a, "skill_b": b, "co_jobs": c} for (a, b), c in pairs.items()]
    return pd.DataFrame(rows).sort_values("co_jobs", ascending=False).head(25) if rows else pd.DataFrame(columns=["skill_a", "skill_b", "co_jobs"])


SKILL_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "ms excel": "Excel",
    "excel": "Excel",
    "sql": "SQL",
    "mysql": "MySQL",
    "python": "Python",
    "java": "Java",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "machine learning": "Machine Learning",
    "scikit-learn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tableau": "Tableau",
    "spark": "Apache Spark",
    "kafka": "Apache Kafka",
    "airflow": "Apache Airflow",
    "docker": "Docker",
    "git": "Git",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "llm": "LLM",
    "rag": "RAG",
}


def extract_skills(text: str, known_skills: Iterable[str]) -> list[str]:
    lower = (text or "").lower()
    hits: list[str] = []
    for raw in known_skills:
        if raw.lower() in lower:
            hits.append(raw)
    for needle, canonical in SKILL_ALIASES.items():
        if re.search(r"\b" + re.escape(needle) + r"\b", lower) and canonical not in hits:
            hits.append(canonical)
    return sorted(set(hits))


def skill_gap(jobs: pd.DataFrame, skills: pd.DataFrame, target_role: str, user_skills: Iterable[str]) -> pd.DataFrame:
    subset = jobs[jobs["title"].str.contains(re.escape(target_role), case=False, na=False)]
    target = skill_matrix(subset, skills)
    if target.empty:
        return target
    user = {s.lower().strip() for s in user_skills if s.strip()}
    target["has_skill"] = target["skill"].str.lower().isin(user)
    target["priority_score"] = (target["demand_share"] * 100).round(2)
    return target.sort_values(["has_skill", "priority_score"], ascending=[True, False])
