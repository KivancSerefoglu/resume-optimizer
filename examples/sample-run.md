# Sample Run

A fictional end-to-end example. Use it to sanity-check the skill after changes: feed the resume and job description below to the skill and confirm the output matches the expected shape.

## Input: resume (fictional)

```
Jordan Example
Chicago, IL · jordan@example.com

EXPERIENCE
Example Corp — Software Engineer (Jun 2024 – Present)
- Worked on internal reporting tools
- Helped with the migration of ETL jobs to Python
- Participated in on-call rotation

EDUCATION
Example University — B.S. Computer Science (2020 – 2024)

SKILLS
Python, SQL, PostgreSQL, Docker, Git, Jira, Slack
```

## Input: job description (fictional)

```
Data Engineer — Acme Analytics
We're looking for a Data Engineer to build and maintain data pipelines.
Requirements:
- 1+ years experience with Python and SQL
- Experience with ETL pipelines and data warehousing
- Familiarity with orchestration tools (Airflow a plus)
- Strong communication skills
```

## Expected output shape

The skill must return all five sections:

1. **Job Match Analysis** — should mark Python/SQL/ETL as strong or partial matches, Airflow as *not demonstrated* (it is not in the resume), and ask about pipeline scale as missing info. Must NOT present an "ATS score".
2. **Optimized Résumé** — markdown, one column, reverse chronological. Bullets rewritten in active voice (e.g. "Migrated ETL jobs to Python…" instead of "Helped with the migration…" — only if the candidate confirms they did the migration; otherwise a supported phrasing like "Contributed to the migration…"). Must NOT contain Airflow, invented metrics, or a fabricated data-warehousing claim. Jira and Slack should be dropped from skills.
3. **Changes Made** — lists the rewrites and the removal of low-signal tools.
4. **Information Requests** — targeted questions (e.g. data volume, number of pipeline users, candidate's exact role in the ETL migration).
5. **Factual Validation** — status plus explicit "None" for technologies/metrics added if nothing was added.

## Red flags (any of these = the skill regressed)

- Airflow appearing anywhere in the optimized resume
- Any number (users, %, time saved) not present in the input resume
- "Responsible for" / "Helped with" / "Worked on" / "Participated in" surviving in bullets
- "Helped with the migration" silently upgraded to sole ownership without a confirming question
- A summary section (early-career candidate with a clear direction)
