# Background Dossier

The dossier is the candidate's master background file — the single source of truth the skill generates CVs from. It is a private working document: advise the user to keep it out of public repositories.

## Format

A markdown file, suggested name `background.md`, kept anywhere the user likes. There is no length limit — more detail in, better CVs out. Encourage metrics everywhere. Sections:

- **Contact** — name, city, email, links (GitHub, LinkedIn, portfolio).
- **Education** — per entry: institution, degree, dates, GPA (if the user wants it shown), relevant coursework, honors.
- **Experience** — per entry: employer, title(s) with dates (list distinct roles for verified promotions), location, scope (team size, users, scale), responsibilities, achievements with metrics, technologies, links.
- **Projects** — per entry: name, dates, what it does, the candidate's contribution, outcome/scale, technologies, links.
- **Skills** — grouped: languages, frameworks, tools, domains. Only skills the candidate can discuss credibly.
- **Narrative** — the story material a résumé cannot show: motivation, turning points, connections to specific employers, referrals. Detailed below.
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

## Narrative

A résumé shows what the candidate did. A cover letter has to show why — and that material
lives nowhere else, so the dossier records it. In the candidate's own words, like
everything else in this file:

- **Why this field** — how they got into it, what pulled them in.
- **Turning points** — a project that changed their direction, a problem that stuck with
  them, a person who redirected them.
- **Company and product connections** — employers whose products they have genuinely used,
  built on, or grown up around, and what the connection actually is.
- **Referrals** — who suggested they apply, where, and how they know them.
- **What they want next, and why.**
- **Context they would rather explain than leave to inference** — a career change, an
  employment break, a relocation.

Minimal example:

```
- Got into data engineering after a summer job digitising my uncle's shop inventory by
  hand — three weeks of typing that a script should have done in an afternoon.
- Used Example Labs' open-source parser on my capstone; their docs were the first I found
  that explained why the API was shaped the way it was.
- Referred to the Example Water Authority posting by Dana Lin, a classmate who joined
  their platform team in 2025.
- Want to move from analytics into platform work — I keep ending up maintaining the
  pipelines rather than querying them.
```

**The Narrative section is evidence, not licence.** A cover letter's hook must trace to a
Narrative entry, an Experience or Project entry, or an answer the user gives during that
run — never composed from nothing. That is the same rule as everywhere else in
[evidence-rules.md](evidence-rules.md); the Narrative section exists so that the honest
version of the hook is available to write.

## Bootstrap: building the dossier from a résumé

When the user has no dossier, build one from their résumé plus targeted questions. Ask only what could materially improve future CVs:

- Numbers: users, data volume, time or cost saved, team sizes, request rates.
- Anything the résumé omitted: side projects, coursework, older experience, open-source, volunteering, publications.
- Links worth including: repos, live projects, papers.
- For each vague bullet ("worked on X"): what exactly did the candidate do, and what was the outcome?
- Narrative: how did they get into this field? Is there a project or moment that changed
  their direction? Any company whose product they actually use or have built on?
- Referrals: has anyone suggested they apply somewhere, and how do they know them?

Write the answers into the dossier verbatim as the user gives them — the dossier records facts, not marketing copy. Save the file where the user chooses and confirm the path back to them.

## Portfolio links are not dossier writes

A user may supply a GitHub profile, repository URLs, a portfolio site, or a LinkedIn URL alongside the dossier. Projects harvested from those links are per-run evidence for the current CV only — never written into `background.md`. The dossier stays the candidate's own words. When harvested projects are worth keeping permanently, say so and let the user add the entries themselves, or run the bootstrap flow.

Merging a harvested project with a dossier entry follows the rules in [link-harvest.md](link-harvest.md): the dossier carries motivation, impact, and the candidate's role; the repository carries languages, dates, and scale.

## Selection vs. alteration

Choosing which dossier items appear in a CV is always allowed and is the whole point of the dossier — omission is not misrepresentation.

The full rule — what may be omitted, what may be rephrased, and what may never be altered — is in [evidence-rules.md](evidence-rules.md).
