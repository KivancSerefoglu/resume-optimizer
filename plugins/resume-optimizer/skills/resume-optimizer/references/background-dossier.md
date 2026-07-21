# Background Dossier

The dossier is the candidate's master background file — the single source of truth the skill generates CVs from. It is a private working document: advise the user to keep it out of public repositories.

## Format

A markdown file, suggested name `background.md`, kept anywhere the user likes. There is no length limit — more detail in, better CVs out. Encourage metrics everywhere. Sections:

- **Contact** — name, city, email, links (GitHub, LinkedIn, portfolio).
- **Education** — per entry: institution, degree, dates, GPA (if the user wants it shown), relevant coursework, honors.
- **Experience** — per entry: employer, title(s) with dates (list distinct roles for verified promotions), location, scope (team size, users, scale), responsibilities, achievements with metrics, technologies, links.
- **Projects** — per entry: name, dates, what it does, the candidate's contribution, outcome/scale, technologies, links.
- **Skills** — grouped: languages, frameworks, tools, domains. Only skills the candidate can discuss credibly.
- **Awards & Publications** — awards, publications, patents, talks, with dates and venues.
- **Extras** — volunteering, spoken languages, certifications, work authorization (recorded only if the user wants it considered in applications).

Minimal example of one Experience entry:

```
### Example Corp — Software Engineer (Jun 2024 – Present), Chicago, IL
- Team of 6 engineers; internal data-platform group
- Migrated 12 nightly ETL jobs from Bash to Python, roughly halving failure rate
- Built reporting dashboard used by 3 teams (Python, PostgreSQL)
- Technologies: Python, PostgreSQL, Docker, GitHub Actions
```

## Bootstrap: building the dossier from a résumé

When the user has no dossier, build one from their résumé plus targeted questions. Ask only what could materially improve future CVs:

- Numbers: users, data volume, time or cost saved, team sizes, request rates.
- Anything the résumé omitted: side projects, coursework, older experience, open-source, volunteering, publications.
- Links worth including: repos, live projects, papers.
- For each vague bullet ("worked on X"): what exactly did the candidate do, and what was the outcome?

Write the answers into the dossier verbatim as the user gives them — the dossier records facts, not marketing copy. Save the file where the user chooses and confirm the path back to them.

## Selection vs. alteration

- Choosing which dossier items appear in a CV is always allowed and is the whole point of the dossier — omission is not misrepresentation.
- Rephrasing an included item per the writing guide is allowed.
- Altering any fact inside an included item — dates, titles, metrics, technologies, scope — is never allowed. If an item is worth including but weak as stated, include it accurately or ask the user for the missing detail.
