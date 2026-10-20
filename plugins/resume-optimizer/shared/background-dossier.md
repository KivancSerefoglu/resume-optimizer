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
- **Extras** — volunteering, spoken languages, certifications, work authorization (recorded only if the user wants it considered in applications; a Preferences entry wins when both exist).
- **Preferences** — the candidate's standing choices about how applications are produced: page size, page limit, languages, items never printed, items never trimmed, deal-breakers. Detailed below.

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

## Preferences

Facts say what the candidate has done. Preferences say how they want their applications
produced, and they hold across every run, so they belong in the dossier rather than in
each conversation. One labelled line per field, free text after the label. Every field is
optional; when the section or a field is absent, the default applies.

```
## Preferences
- Page size: Letter
- Resume page limit: 1
- CV language: English
- Letter language: English
- Never printed: GPA
- Never trimmed: personal website link
- Work authorization to consider: US citizen
- Target company types: technology-first product companies, research labs
- Deal-breakers: fully on-site outside Chicago; no sponsorship when sponsorship is needed
```

| Field | Default | What it controls |
|---|---|---|
| Page size | Letter | `A4` or `Letter`; passed to the renderer for both the résumé and the letter |
| Resume page limit | 1 | The hard page limit the résumé trim loop enforces against the rendered PDF |
| CV language | English | Recorded for later use; in this version the résumé is written in English only, because the character-set rule and the ATS check are ASCII-based |
| Letter language | English | The language the cover letter is written in |
| Never printed | (none) | Items that never reach any page, whatever the posting asks for — GPA, a photo, a home address |
| Never trimmed | (none) | Items that survive every trim pass; when protecting one forces a different cut, the user is told which |
| Work authorization to consider | (none) | Informs the match analysis and the verdict; never appears on the résumé |
| Target company types | (none) | Informs tailoring register and the positioning advice |
| Deal-breakers | (none) | Conditions that make a role not worth applying to; a posting that states one is a Skip, and the verdict names it |

Four rules:

1. **Read silently, ask only for gaps.** A skill reads this section before asking any
   application-context question, and asks only about fields the section does not cover.
   Never re-ask for a preference the dossier states.
2. **Choices, not evidence.** A preference is never a fact about the candidate. "Target
   company types: research labs" says nothing about research experience.
3. **Never printed outranks the posting.** A posting that asks for a GPA does not put a
   GPA on a page when the dossier says never.
4. **Never trimmed survives every rung.** The trim ladder skips a protected item at every
   step. When that protection forces a different cut — coursework goes before the
   website link, for instance — the user is told so in Changes Made.

## Bootstrap: building the dossier from a résumé

When the user has no dossier, build one from their résumé plus targeted questions. Ask only what could materially improve future CVs:

- Numbers: users, data volume, time or cost saved, team sizes, request rates.
- Anything the résumé omitted: side projects, coursework, older experience, open-source, volunteering, publications.
- Links worth including: repos, live projects, papers.
- For each vague bullet ("worked on X"): what exactly did the candidate do, and what was the outcome?
- Narrative: how did they get into this field? Is there a project or moment that changed
  their direction? Any company whose product they actually use or have built on?
- Referrals: has anyone suggested they apply somewhere, and how do they know them?
- Preferences: A4 or Letter, and how many pages? Which language for the letter? Anything
  that should never be printed, or never cut? Any deal-breaker that makes a role not
  worth applying to?

Write the answers into the dossier verbatim as the user gives them — the dossier records
facts, not marketing copy; the same rule governs facts confirmed later, in
[evidence-rules.md](evidence-rules.md#facts-confirmed-during-a-run). Save the file where
the user chooses and confirm the path back to them.

## Portfolio links are not dossier writes

A user may supply a GitHub profile, repository URLs, a portfolio site, or a LinkedIn URL alongside the dossier. Projects harvested from those links are per-run evidence for the current CV only — never written into `background.md`. The dossier stays the candidate's own words. When harvested projects are worth keeping permanently, say so and let the user add the entries themselves, or run the bootstrap flow.

Merging a harvested project with a dossier entry follows the rules in [link-harvest.md](link-harvest.md): the dossier carries motivation, impact, and the candidate's role; the repository carries languages, dates, and scale.

## Selection vs. alteration

Choosing which dossier items appear in a CV is always allowed and is the whole point of the dossier — omission is not misrepresentation.

The full rule — what may be omitted, what may be rephrased, and what may never be altered — is in [evidence-rules.md](evidence-rules.md).
