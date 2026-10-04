# Interview guide

## 1. Why did you separate jobs and skills into two tables?
Because a job can require many skills and a skill can occur in many jobs. This many-to-many relationship is cleaner, queryable, and scalable as a bridge table.

## 2. Why start with SQLite?
It keeps the project completely free and local. The schema is relational, so the same tables can move to PostgreSQL with minimal conceptual change.

## 3. How do you avoid double-counting skill demand?
Demand is measured as the number of distinct job postings linked to a skill, not raw keyword occurrences in the description.

## 4. What is the skill-gap score?
It is a prioritization heuristic based on the share of target-role postings requiring each skill. It helps rank learning priorities; it is not a hiring-probability model.

## 5. How would you productionize it?
Replace SQLite with PostgreSQL, schedule ingestion with Airflow, add data-quality checks, store raw data in object storage, transform with dbt, containerize services, and add monitoring.

## 6. How would you handle duplicate postings?
Create a canonical source-specific key where possible, then add fuzzy matching on normalized title/company/location/date as a second-stage deduplication strategy.

## 7. How would you improve salary analytics?
Normalize currency, use explicit salary periods, distinguish disclosed from inferred salary, winsorize extreme values, and report sample sizes and confidence intervals.

## 8. What are the risks of job-board data?
Terms of service, robots rules, duplicate listings, stale listings, missing salary data, inconsistent titles, and selection bias. Use authorized APIs/public datasets wherever possible.

## 9. How would you test the pipeline?
Schema validation, null/range checks, uniqueness tests, row-count anomaly checks, unit tests for transformations, and end-to-end ingestion tests.

## 10. What is the most important product insight?
The value is not just a list of jobs; it is the translation from market demand into a specific action, such as which skill to learn next for a target role.
