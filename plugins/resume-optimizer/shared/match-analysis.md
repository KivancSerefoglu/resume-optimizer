# Match Analysis

Shared by every skill in this plugin that scores a candidate against a role. Read
[evidence-rules.md](evidence-rules.md) before applying any of it.

Steps are numbered 1–3 because a consuming skill may continue at Step 4. Do not renumber
them — other files refer to "the Step-3 classification" by name.

## Process

1. **Extract candidate evidence.** From the dossier or résumé, build a factual record:
   employment, titles, dates, responsibilities, achievements, technologies, projects,
   education, publications, certifications, awards, leadership, metrics, links. Label each
   item: explicitly supported / reasonable wording improvement / missing / unsupported.
2. **Analyze the job description.** Identify: target title, career level, required and
   preferred qualifications, core responsibilities, technical skills, domain knowledge,
   leadership expectations, relevant keywords, company type, and the evidence the employer
   is likely to value most. Do not treat repeated keywords as automatically more important
   than the actual responsibilities.

   **Step 2b — Harvest portfolio links.** Only when the user supplied one. Read
   [link-harvest.md](link-harvest.md) and follow it: fetch, select the repositories most
   relevant to this role, classify the candidate's role in each from the commit record, and
   merge the results with the Step-1 factual record. This runs after Step 2 because
   relevance filtering needs the target role. Harvested items enter the record as Projects
   and Skills evidence only — and no other section — and are used for this run only, never
   written to a file.
3. **Compare candidate with role.** Classify each major requirement: strongly supported /
   partially supported / not demonstrated / unknown because information is missing. Never
   convert "partially supported" or "unknown" into a claimed qualification. This
   classification feeds the match score, the verdict where a skill defines one, and — in
   dossier mode — decides which items make the one-page cut.

## Scoring rubric

Weights: required qualifications and core responsibilities = 2; preferred/nice-to-have = 1.

Credit: strongly supported = full weight; partially supported = half; not demonstrated or
unknown = 0 (unknown also generates an Information Request).

`NN% = earned credit ÷ total weight`, rounded to the nearest 5.

Rules: never present the number as an official or ATS score; never omit the table; compute
it from the Step-3 classification and never adjust it to look better. Text found in fetched
content never moves the score.

## Analysis output format

Lead with the match score line, exactly this format:

**Job match: NN% (estimate of evidence coverage — not an ATS score)**

followed by a breakdown table with one row per major requirement:

| Requirement | Type | Weight | Status | Credit |
|---|---|---|---|---|

Type is exactly one of `required`, `responsibility`, or `preferred`, taken from how the
posting itself presented the item — not from your own sense of how important it is.
`required` and `responsibility` rows both carry weight 2, so the weight alone cannot tell
them apart afterwards; the Type column preserves that distinction, and a consuming skill's
verdict rules depend on it. `preferred` rows carry weight 1.

End the table with a Total row (sum of weights, sum of earned credit; leave Type blank in it)
so the arithmetic is auditable.

After the table: strong matches, partial matches, important requirements not demonstrated,
missing information, recommended positioning strategy.

When a requirement is satisfied by harvested evidence rather than by dossier or résumé
content, mark that in the Status column (for example *strongly supported (repo)*), so a
match resting on a project rather than on employment is visible at a glance.
