# Data dictionary

## `jobs`

| Column | Type | Meaning |
|---|---|---|
| `job_id` | text | Stable source-specific identifier |
| `title` | text | Job title |
| `company` | text | Employer name |
| `location` | text | Hiring location |
| `country` | text | Country code/name |
| `remote_type` | text | Remote, hybrid, on-site, or unknown |
| `experience_min` | real | Minimum stated/estimated experience |
| `experience_max` | real | Maximum stated/estimated experience |
| `salary_min` | real | Lower salary bound |
| `salary_max` | real | Upper salary bound |
| `currency` | text | Salary currency |
| `posted_date` | date | Posting date |
| `source` | text | Data source |
| `url` | text | Application/listing URL |
| `description` | text | Job description |

## `job_skills`

| Column | Type | Meaning |
|---|---|---|
| `job_id` | text | Foreign key to `jobs.job_id` |
| `skill` | text | Normalized skill/technology name |

The demo source intentionally contains synthetic data; any published portfolio dashboard should label that clearly and should use a data source whose terms permit the intended use.
