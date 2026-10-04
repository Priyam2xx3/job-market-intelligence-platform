from __future__ import annotations

import re

import pandas as pd
import plotly.express as px
import streamlit as st

from app.analytics import (
    add_salary_metrics,
    cooccurrence,
    extract_skills,
    location_summary,
    monthly_trend,
    role_summary,
    skill_gap,
    skill_matrix,
    top_skills,
)
from app.db import get_connection, init_db

st.set_page_config(page_title="Job Market Intelligence", page_icon="📊", layout="wide")

init_db()

@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    with get_connection() as conn:
        jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
        skills = pd.read_sql_query("SELECT * FROM job_skills", conn)
    return add_salary_metrics(jobs), skills

jobs, skills = load_data()

st.markdown("# 📊 Job Market Intelligence Platform")
st.caption("Explore job demand, salaries, locations, skill combinations, and personalized skill gaps.")

if jobs.empty:
    st.warning("No jobs found. Run `python scripts/generate_demo_data.py` followed by `python scripts/ingest_jobs.py --input data/jobs.csv`.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    role_options = ["All"] + sorted(jobs["title"].dropna().unique().tolist())
    selected_role = st.selectbox("Target role", role_options)
    location_options = ["All"] + sorted(jobs["location"].dropna().unique().tolist())
    selected_location = st.selectbox("Location", location_options)
    remote_options = ["All"] + sorted(jobs["remote_type"].dropna().unique().tolist())
    selected_remote = st.selectbox("Work mode", remote_options)
    min_exp, max_exp = st.slider("Experience range (years)", 0, 10, (0, 6))

filtered = jobs.copy()
if selected_role != "All":
    filtered = filtered[filtered["title"].eq(selected_role)]
if selected_location != "All":
    filtered = filtered[filtered["location"].eq(selected_location)]
if selected_remote != "All":
    filtered = filtered[filtered["remote_type"].eq(selected_remote)]
filtered = filtered[(filtered["experience_min"] <= max_exp) & (filtered["experience_max"] >= min_exp)]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Jobs", f"{len(filtered):,}")
k2.metric("Median salary", f"₹{filtered['salary_mid'].median()/100000:.1f}L" if not filtered.empty else "—")
k3.metric("Median experience", f"{filtered['experience_mid'].median():.1f} yrs" if not filtered.empty else "—")
k4.metric("Companies", f"{filtered['company'].nunique():,}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Skills", "Roles & Locations", "Job Explorer", "Skill Gap"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        trend = monthly_trend(filtered)
        st.plotly_chart(px.line(trend, x="month", y="job_count", markers=True, title="Hiring volume trend"), use_container_width=True)
    with c2:
        remote = filtered["remote_type"].value_counts().rename_axis("work_mode").reset_index(name="jobs")
        st.plotly_chart(px.pie(remote, names="work_mode", values="jobs", title="Work-mode mix"), use_container_width=True)

    summary = role_summary(filtered)
    st.dataframe(summary, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Most requested skills")
    filtered_skill_ids = set(filtered["job_id"])
    target_skills = skills[skills["job_id"].isin(filtered_skill_ids)]
    skill_counts = top_skills(filtered, target_skills, limit=20)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(skill_counts.sort_values("job_count"), x="job_count", y="skill", orientation="h", title="Skill demand"), use_container_width=True)
    with right:
        pairs = cooccurrence(target_skills)
        if pairs.empty:
            st.info("Not enough skill data for co-occurrence analysis.")
        else:
            pairs["pair"] = pairs["skill_a"] + " + " + pairs["skill_b"]
            st.plotly_chart(px.bar(pairs.sort_values("co_jobs"), x="co_jobs", y="pair", orientation="h", title="Skills that appear together"), use_container_width=True)

    st.subheader("Skill coverage by target role")
    role = selected_role if selected_role != "All" else st.selectbox("Analyze a role", sorted(jobs["title"].unique()), key="skills_role")
    matrix = skill_matrix(jobs, skills, role)
    matrix["demand_share"] = (matrix["demand_share"] * 100).round(1)
    st.dataframe(matrix.head(20).rename(columns={"demand_share": "share_of_jobs_pct"}), use_container_width=True, hide_index=True)

with tab3:
    left, right = st.columns(2)
    with left:
        loc = location_summary(filtered).head(15)
        st.plotly_chart(px.bar(loc.sort_values("job_count"), x="job_count", y="location", orientation="h", title="Top hiring locations"), use_container_width=True)
    with right:
        salary = filtered.groupby("title", as_index=False)["salary_mid"].median().sort_values("salary_mid", ascending=False)
        st.plotly_chart(px.bar(salary, x="salary_mid", y="title", orientation="h", title="Median salary by role"), use_container_width=True)

    st.subheader("Location intelligence")
    st.dataframe(location_summary(filtered), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Search the job market")
    q = st.text_input("Search titles, companies, or descriptions")
    explorer = filtered.copy()
    if q.strip():
        pattern = re.escape(q.strip())
        mask = explorer["title"].str.contains(pattern, case=False, na=False) | explorer["company"].str.contains(pattern, case=False, na=False) | explorer["description"].str.contains(pattern, case=False, na=False)
        explorer = explorer[mask]
    display_cols = ["title", "company", "location", "remote_type", "experience_min", "experience_max", "salary_min", "salary_max", "posted_date", "source", "url"]
    st.dataframe(explorer[display_cols].sort_values("posted_date", ascending=False).head(200), use_container_width=True, hide_index=True, column_config={"url": st.column_config.LinkColumn("Apply")})
    st.download_button("Download filtered jobs", explorer.to_csv(index=False).encode("utf-8"), "filtered_jobs.csv", "text/csv")

with tab5:
    st.subheader("Personal skill-gap analyzer")
    default_role = selected_role if selected_role != "All" else "Data Analyst"
    target_role = st.selectbox("Target role", sorted(jobs["title"].unique()), index=sorted(jobs["title"].unique()).index(default_role) if default_role in jobs["title"].unique() else 0, key="gap_role")
    skills_text = st.text_area("Your current skills", placeholder="Example: SQL, Excel, Power BI, Java, Git")
    resume_text = st.text_area("Or paste a resume / profile summary", height=130, placeholder="Paste your resume text here. The app will detect matching skills.")

    known = sorted(set(skills["skill"].tolist()))
    typed = [s.strip() for s in skills_text.split(",") if s.strip()]
    detected = extract_skills(resume_text, known)
    combined = sorted(set(typed + detected), key=str.lower)
    if combined:
        st.success("Detected skills: " + ", ".join(combined))
    result = skill_gap(jobs, skills, target_role, combined)
    missing = result[~result["has_skill"]].head(10) if not result.empty else pd.DataFrame()
    present = result[result["has_skill"]].head(10) if not result.empty else pd.DataFrame()

    a, b = st.columns(2)
    with a:
        st.markdown("### Priority skills to learn")
        if missing.empty:
            st.info("Enter your current skills or a resume to generate gaps.")
        else:
            for _, row in missing.iterrows():
                st.write(f"**{row['skill']}** — appears in {row['demand_share']*100:.1f}% of matching jobs")
    with b:
        st.markdown("### Skills you already have")
        if present.empty:
            st.info("Your matched skills will appear here.")
        else:
            st.dataframe(present[["skill", "demand_share"]].assign(demand_share=lambda x: (x["demand_share"]*100).round(1).astype(str)+"%"), use_container_width=True, hide_index=True)

st.divider()
st.caption("Demo dataset is synthetic. Replace it with permitted public/API job data before publishing market statistics.")
