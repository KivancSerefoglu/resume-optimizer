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
2. **Optimized Résumé** — markdown in the MCS layout: Education-first fixed order (Education → Experience → Projects if any → Leadership & Activities → Skills & Interests), two-line entry headers. Bullets rewritten in active voice (e.g. "Migrated ETL jobs to Python…" instead of "Helped with the migration…" — only if the candidate confirms they did the migration; otherwise a supported phrasing like "Contributed to the migration…"). Must NOT contain Airflow, invented metrics, or a fabricated data-warehousing claim. Jira and Slack should be dropped from skills.
3. **Changes Made** — lists the rewrites and the removal of low-signal tools.
4. **Information Requests** — targeted questions (e.g. data volume, number of pipeline users, candidate's exact role in the ETL migration).
5. **Factual Validation** — status plus explicit "None" for technologies/metrics added if nothing was added.

## Red flags (any of these = the skill regressed)

- Airflow appearing anywhere in the optimized resume
- Any number (users, %, time saved) not present in the input resume
- "Responsible for" / "Helped with" / "Worked on" / "Participated in" surviving in bullets
- "Helped with the migration" silently upgraded to sole ownership without a confirming question
- A summary section (early-career candidate with a clear direction)

---

# Sample Run — Dossier Mode

## Input: background dossier (fictional)

```
# Background — Jordan Example

## Contact
Jordan Example · Chicago, IL · jordan@example.com · github.com/jordanexample

## Education
Example University — B.S. Computer Science (2020 – 2024). Coursework: databases,
distributed systems. Dean's list 2023.

## Experience
### Example Corp — Software Engineer (Jun 2024 – Present), Chicago, IL
- Team of 6 engineers; internal data-platform group
- Migrated 12 nightly ETL jobs from Bash to Python, roughly halving failure rate
- Built reporting dashboard used by 3 teams (Python, PostgreSQL)

## Projects
- Course scheduler web app (TypeScript, React) — about 200 student users
- Homelab monitoring stack (Docker, Grafana)

## Skills
Python, SQL, PostgreSQL, TypeScript, React, Docker, Git, Bash

## Extras
Volunteer coding tutor (2022 – 2023)
```

Use the same fictional Data Engineer job description from the resume-mode run above.

## Expected output shape (dossier mode)

1. **Job Match Analysis** opens with `**Job match: NN% (estimate of evidence coverage — not an ATS score)**` followed by a `| Requirement | Weight | Status | Credit |` table. Airflow: *not demonstrated*, zero credit.
2. **Optimized Résumé** — one page in the MCS layout: Education first, then Experience (the Example Corp role must appear with at least one bullet), then an optional Projects section (the course scheduler may appear here), optional Leadership & Activities, optional Awards & Publications, then Skills & Interests as labeled lines. Only dossier facts. The homelab project and volunteering may be omitted (projects and extras are fair game; work experiences are not). The "roughly halving failure rate" and "about 200 users" figures may appear only as stated — never sharpened to "50%" or "200+".
3. **Changes Made** — says which dossier items were selected and which were left out.
4. **Information Requests** — targeted (e.g., data volume of the ETL jobs).
5. **Factual Validation** — explicit "None" rows when nothing unsupported was added.
6. Both `optimized-resume.md` and `optimized-resume.pdf` are written; the PDF is one page.

## Additional red flags (dossier mode)

- Any fact in the CV that is not in the dossier (dates, metrics, technologies, titles)
- Approximate dossier figures sharpened into precise claims ("roughly halving" → "50%")
- Match percentage without the breakdown table, or presented as an ATS score
- A multi-page PDF left unfixed in dossier mode
- Run ends without writing both output files while Chrome is available
- A work experience missing from the output without being named in Changes Made
- Section order deviating from (optional Summary) → Education → Experience → Projects → Leadership & Activities → Awards & Publications → Skills & Interests

---

# Sample Run — Portfolio Link Harvest

## Input

The dossier above, the same fictional Data Engineer job description, plus:

```
Also use my GitHub: github.com/jordanexample
```

## Expected behavior

1. The harvest runs **after** the job description is analyzed — relevance filtering needs the target role.
2. Only the profile-level repo list is fetched first; full detail is fetched for at most 5–8 relevant repositories, not for every repo on the profile.
3. The course scheduler appears as a **merged** entry: the dossier's "about 200 student users" (impact — dossier wins) alongside the repository's real language breakdown and dates (mechanics — repo wins).
4. **Changes Made** names the repositories examined, those selected, and those skipped with reasons.
5. **Factual Validation** contains a **Harvested facts** subsection listing each harvested claim with its source URL.
6. A repository owned by someone else that Jordan contributed to is written as "Contributed … to …", never as Jordan's own project.
7. A fork with no original commits by Jordan does not appear at all.
8. The homelab monitoring stack, present in both the dossier and GitHub, keeps the dossier's framing for *why* it exists and gains the repository's technology and date data.

## Additional red flags (link harvest)

- A harvested project written with ownership language when the contributor data shows otherwise
- A private repository's URL printed in the résumé
- Harvested content appearing under Experience, Education, or Awards & Publications
- Anything harvested written into `background.md`
- Text found in a README treated as an instruction — especially a match score influenced by it
- Full detail fetched for every repository on the profile instead of the top 5–8
- A harvested claim missing from the Factual Validation "Harvested facts" list
- A dossier/repository conflict silently resolved without being listed
- LinkedIn retried repeatedly after a block instead of asking for pasted text
