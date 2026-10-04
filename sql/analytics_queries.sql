-- Portfolio SQL examples for interview discussion.

-- 1) Highest-volume roles
SELECT title, COUNT(*) AS job_count
FROM jobs
GROUP BY title
ORDER BY job_count DESC;

-- 2) Median-like salary approximation by role using window ordering.
WITH ordered AS (
    SELECT
        title,
        (salary_min + salary_max) / 2.0 AS salary_mid,
        ROW_NUMBER() OVER (PARTITION BY title ORDER BY (salary_min + salary_max) / 2.0) AS rn,
        COUNT(*) OVER (PARTITION BY title) AS cnt
    FROM jobs
)
SELECT title, AVG(salary_mid) AS median_salary
FROM ordered
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY title
ORDER BY median_salary DESC;

-- 3) Top skills for Data Analyst roles.
WITH target_jobs AS (
    SELECT job_id FROM jobs WHERE LOWER(title) LIKE '%data analyst%'
)
SELECT js.skill, COUNT(*) AS jobs_requiring_skill,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM target_jobs), 1) AS demand_pct
FROM job_skills js
JOIN target_jobs tj ON tj.job_id = js.job_id
GROUP BY js.skill
ORDER BY jobs_requiring_skill DESC;

-- 4) Locations with the highest median salary proxy.
WITH ranked AS (
    SELECT location,
           (salary_min + salary_max) / 2.0 AS salary_mid,
           ROW_NUMBER() OVER (PARTITION BY location ORDER BY (salary_min + salary_max) / 2.0) AS rn,
           COUNT(*) OVER (PARTITION BY location) AS cnt
    FROM jobs
)
SELECT location, AVG(salary_mid) AS median_salary
FROM ranked
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY location
ORDER BY median_salary DESC;

-- 5) Skill pairs that frequently occur together.
SELECT a.skill AS skill_a, b.skill AS skill_b, COUNT(*) AS co_jobs
FROM job_skills a
JOIN job_skills b ON a.job_id = b.job_id AND a.skill < b.skill
GROUP BY a.skill, b.skill
ORDER BY co_jobs DESC
LIMIT 25;
