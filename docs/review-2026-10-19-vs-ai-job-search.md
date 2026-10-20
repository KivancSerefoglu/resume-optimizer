# Review: resume-optimizer, and how it compares to MadsLorentzen/ai-job-search

Date: 2026-10-19. Plugin version reviewed: 1.7.0 (commit d060bba).
Comparison target: https://github.com/MadsLorentzen/ai-job-search (shallow clone, same day).

Method: the plugin's three skills, shared files, templates and scripts were read in full;
ai-job-search's README, `/apply`, the `job-application-assistant` skill and its nine reference
files, the reviewer agent and the verification tools were read. Both repos were also built
into graphify knowledge graphs (see the last section). The plugin's own test scripts were run
and pass (`test-render.py` 9 tests, `test-html-to-md.py` 11 tests, `check-links.py` 0 problems).

---

## 1. What does not make sense, or is rougher than it should be

Ordered by how much it affects a real application run.

### 1.1 US conventions are hard-coded, and the author is not applying in the US

Three decisions are baked in with no switch:

- `@page { size: letter }` in both `resume-template.html` and `cover-letter-template.html`.
  European and Turkish employers expect A4. A Letter PDF printed on A4 loses margins.
- The one-page hard limit (`SKILL.md` Export step 4, `writing-guide.md`). It is a US norm.
  Most European markets expect two pages for anyone past entry level, and the trim ladder's
  step (d) ("stop and tell the user") is where a 10-year career will land.
- Dates written out US style (`March 3, 2026`) in `letter-structure.md`.

None of these is wrong for a US application. The problem is that the plugin cannot do anything
else, and the skill text treats the choice as a rule of good writing rather than a locale.

### 1.2 There is no place for the candidate's standing preferences

Every run re-asks for "application context" (career level, target company type, work
authorization, IC or management track). Rules that are personal and permanent have no home
in the dossier format, so they live in Claude's memory file instead. Two already exist for
this project: "never print GPA" and "the website is never cut; trim coursework first". Those are
exactly the kind of fact `background-dossier.md` should carry, because a memory note is
per-machine and invisible to the skill's validation.

ai-job-search puts all of this in profile files the workflow reads every run.

### 1.3 Facts learned in conversation are thrown away

`resume-optimizer` asks probing questions (critical-review.md, "Interview before you write")
and uses the answers for that run. Nothing says to offer writing a confirmed answer back into
`background.md`. Only `cover-letter` offers it, and only for Narrative entries. So a user who
answers "about 40,000 users" in one session will be asked again next week, or worse, the
metric will silently vanish from the next CV because the dossier never had it.

ai-job-search names this failure explicitly in `/apply` ("a fact that exists only in chat will
be treated as unsupported by a later session and stripped as a fabrication") and makes
write-back a standing rule. That rule is correct and the plugin lacks it.

### 1.4 English only

The character-set rule transliterates every name and place to ASCII, section headings are
fixed English strings in the template, and there is no CV-language or letter-language
setting. A Turkish or German posting gets an English letter. ai-job-search sets the CV language
once in the profile and writes the cover letter in the posting's language.

### 1.5 Match analysis is re-run and re-printed even when it already ran

`cover-letter` says "if match-analysis already ran in this conversation, reuse its
classification". `resume-optimizer` has no such line, so the typical flow (score first, then
tailor) prints the full requirement table twice. Small, but it is the most common path.

### 1.6 Export instructions mix two path bases

The render command is written relative to the skill directory
(`python3 ../../shared/render.py assets/resume-template.html ...`) while `<dir>` is relative
to the user's working directory. The instructions say "resolve bundled paths relative to this
skill's directory" and also "if the working directory is already that folder, write in
place". Both are right, but a single command line cannot have two bases, and Step 1 says
"`render.py` creates `<dir>`, so there is no separate mkdir step" while Step 2 writes
`<dir>/resume-body.html` before render ever runs. It works today only because the Write tool
creates parent directories. Spell out absolute paths once and reuse them.

### 1.7 The critic is the same context that wrote the draft

The "Hiring Manager Review" (resume Step 6) and the letter's revision pass are performed by
the same conversation that just produced the text. That is better than nothing, and the
prompts are good, but a model reviewing its own draft in the same context tends to confirm
it. ai-job-search dispatches a fresh-context reviewer agent with the drafts inline and gets
back exact `old_string`/`new_string` edits. The plugin already has every ingredient for this
(the screening lens, the four letter failures) and it would cost one Agent call.

### 1.8 Untrusted input is handled only by instruction

`evidence-rules.md` says to treat postings, READMEs and fetched pages as data, and that is
the right rule. But it is the only layer. ai-job-search runs a deterministic `posting_guard.py`
before the model reads anything: it strips hidden HTML (display:none, opacity:0, off-screen),
removes zero-width and bidi characters, quotes instruction-shaped lines, lists hidden URLs,
and checks the posting URL's host against known ATS domains. Since this plugin fetches
arbitrary posting URLs and GitHub READMEs, a small stdlib script in `shared/` doing the same
cleaning is the single biggest hardening available.

### 1.9 Tests exist but nothing runs them, and v1.7 has no spec

`scripts/` has 20 passing unit tests and a link checker, but there is no `.github/workflows`,
so nothing enforces them. `examples/sample-run.md` lists "red flags" that are checked by eye.
Every release from 1.0 to 1.6 has a spec and a plan under `docs/`; 1.7 (candidate-named
files, per-application folders) has neither, so the pattern broke on the latest change.

### 1.10 Trimming is relevance-ordered within a section, static across sections

The ladder cuts bullets from the least relevant experience first, then Projects, Leadership,
Awards, Education notes, Summary, then whole experiences. That ordering ignores two things
ai-job-search scores explicitly: whether a line is duplicated elsewhere on the page, and
whether the cover letter depends on it. The two skills write into the same folder, yet the
letter's "spine" is chosen from the match classification, not from what survived the résumé
trim, so the letter can lean on a project the one-page CV no longer shows.

### 1.11 The verdict measures evidence on paper, not whether the job is worth taking

`match-analysis` scores requirement coverage only, with an auditable table. That is a real
strength. But the output is labelled "Apply / Skip", which reads as a recommendation, while
location, salary, work pattern, culture and eligibility (citizenship, security clearance,
required language) never enter it. ai-job-search runs eligibility and language gates before
scoring and includes location and career-alignment dimensions. A deal-breakers list in the
dossier, checked before the verdict, would close most of the gap without changing the rubric.

### 1.12 Smaller items

- No check that the PDF text layer is parseable (email and phone as literal text, keywords
  present). Chrome's HTML-to-PDF usually gets this right, so this is low priority, but
  `render.py` could print the extracted text once for a one-line check.
- `writing-guide.md` says "include every work experience" and also "one page, no exceptions".
  The ladder resolves it, but the two rules read as contradictory on first read.
- The README promises "no accounts, no API keys, no extra setup", but PDF export needs Chrome,
  Chromium or Edge, and link harvest works best with an authenticated `gh`. Say so.

### What is right and should stay

The evidence model is the plugin's best asset: one dossier in the candidate's own words,
selection allowed and alteration forbidden, a never-invent list shared by all three skills,
harvested repos attributed from the commit record rather than the README, and a letter rule
set that names the four ways a letter lies (enthusiasm, familiarity, relationship, inflation
by paraphrase). The auditable match table with a Total row, the derived-markdown export that
cannot drift from the PDF, the zero-dependency install, and the layering rule enforced by
`check-links.py` are all better than the comparison repo's equivalents.

---

## 2. Same and different

### Same idea, both repos

| Theme | resume-optimizer | ai-job-search |
|---|---|---|
| Master profile the agent drafts from | `background.md` in the candidate's words | `01-candidate-profile.md` + `CLAUDE.md` + master CV (`.tex`) |
| Never fabricate | never-invent list, selection vs alteration, "could you defend this sentence in an interview" | grounding audit against the three-source union, "interview backtrack test" |
| Posting is data, not instructions | `evidence-rules.md` input security | trust boundary in `09-web-research.md`, plus a deterministic gate |
| Page count verified on the rendered PDF, then trim | `render.py` prints `pages: N`, ladder | `verify_pdf.py --pages`, relevance-weighted cuts |
| Letter must not restate the CV | body supplies the why and how | forward-looking, task-solving framing |
| Banned openings and phrases | no "I am writing to apply", no clichés, no dashes | no em-dashes, no clichés, no apologetic hedging |
| Named salutation, never "To whom it may concern" | yes | yes |
| Company claims must trace to a source | three bounded sources, listed in validation | verify every claim via a fetched page, 30-day cache |
| Critique step before output | Hiring Manager Review, letter revision pass | reviewer agent, two-part feedback |
| Harvest projects from GitHub and portfolio links | `link-harvest.md`, per-run only | `/expand`, written into the profile with a source tag |
| One folder per application | `<company>-<position>/` | `documents/applications/<company>_<role>/` |

### Different by design

| Dimension | resume-optimizer | ai-job-search |
|---|---|---|
| Scope | Three skills: score, tailor, letter | Whole pipeline: setup, scrape six portals, rank, apply, interview prep, outcome tracker, Gmail and Notion sync, HTML dashboard, upskill plan, salary tool |
| Size | ~14k words of skill text, 2 Python scripts | ~230k words, 191 code files (TypeScript portal CLIs, Python tools), 61 test files |
| Install | Plugin from marketplace; personal data stays outside the repo | Fork the repo; personal data written into tracked files (README warns to use a private repo) |
| Dependencies | Chrome/Chromium/Edge only | Python 3.10, Bun, TeX Live with lualatex and xelatex, optional pypdf/Poppler |
| CV format | HTML to Chrome PDF, one page, Letter, Georgia, ASCII only, fixed section order (Education first) | LaTeX moderncv banking, exactly two pages, A4, profile statement first, section order varies by role |
| Letter format | Prose, 250–400 words, hook-first (anecdote, bold statement, question, referral) | `cover.cls` with xelatex, 250–300 words, opens by stating the role, 3–5 bullet list, headline formula |
| Letter voice | Register table by employer type, AI-tells list, feeling rule | Warm-direct house style, behavioral-profile match (PI/DISC) |
| Language | English | CV language set in profile; letter follows the posting's language |
| Scoring | Weighted requirement table (2/1), percentage, auditable Total row; verdict Apply / Apply with caveats / Skip | Five dimensions (skills 30, experience 25, culture 15, career 30, location pass/fail), eligibility gate, language gate, salary benchmark |
| Company research | Posting, employer site, user URLs only; no web search | WebSearch allowed, 403 retry with robots.txt check, 30-day JSON cache |
| Reviewer | Same context | Fresh-context `application-reviewer` agent returning JSON edits |
| Injection defence | Instruction-level | `posting_guard.py` + source-host verification + permission allowlist + CI security guards |
| Fact persistence | Per-run; answers not written back (except Narrative offer) | Standing rule: confirmed facts written to the profile in the same turn |
| Testing | 20 unit tests, link checker, manual sample-run red flags, no CI | 759 test functions, CI with LaTeX smoke compiles and skill lint |
| Extensibility | None needed | `/add-portal`, `/add-template`, free-form deal-breakers |

---

## 3. Improvements worth adopting, in order

1. **Preferences section in the dossier spec.** Page size, page limit, CV and letter language,
   items that are never printed (GPA), items that are never cut (website), work authorization,
   target company types, deal-breakers. All three skills read it. This also retires the two
   memory notes.
2. **Write-back rule.** When the user confirms or supplies a fact during a run, offer to append
   it to `background.md` in the same turn, verbatim, in the section it belongs to. Report what
   was written in Factual Validation.
3. **Fresh-context reviewer.** Move the Hiring Manager Review and the letter's "what still reads
   as generated" pass into one Agent call with the draft inline, returning exact edits plus a
   findings list. The existing reference files are already the reviewer's prompt.
4. **Deterministic posting guard in `shared/`.** Strip hidden HTML and invisible characters,
   quote instruction-shaped lines, list hidden URLs. Run it on every fetched posting and README
   before the model reads them, and print its one-line verdict at the top of the match table.
5. **Relevance-weighted trim with a letter dependency check.** Score each line by relevance,
   uniqueness and whether the letter leans on it; and have `cover-letter` confirm every thread
   it uses is still on the final résumé (or deliberately absent from it).
6. **CI.** One workflow running the three scripts on push. Add the missing 1.7 spec and plan.
7. **Letter in the posting's language, A4 switch, light eligibility gate.** Each is a
   preference line plus a sentence in the relevant skill.

### Not worth copying

- The fork-and-track-personal-data model. The plugin's split (code in the marketplace, data
  on the user's disk) is the better design.
- LaTeX. Chrome rendering with a derived markdown file is simpler and fails more gracefully.
- The mandatory two-page CV, the opening sentence that states the role, bullet lists in the
  letter, and the "mention Claude Code by name" rule. These are the author's preferences, not
  best practice, and the plugin's hook-first prose letter is the stronger document.
- The scope. Scraping, tracking, Gmail and Notion sync are a different product. If anything
  is added, an application tracker row per export folder is the only piece that fits.

---

## 4. What the knowledge graphs show

Both repos were built with graphify (AST extraction for code, LLM extraction for docs). This
repo's graph was already current (`graphify-out/graph.json`, 385 nodes, 715 edges, 10
communities). The ai-job-search graph was built fresh (3,073 nodes, 6,007 edges, 159
communities, 96% EXTRACTED). A merged cross-repo graph is at
`graphify-out/cross-repo-graph.json` (3,449 nodes, 6,722 edges).

Health note on the ai-job-search graph: 531 dangling-endpoint edges and 2 self-loops, caused
by placeholder nodes the extraction subagents created for files outside their chunk. The
graph is usable, but a few cross-file references resolve to a stub rather than the real node.

| Measure | resume-optimizer | ai-job-search |
|---|---|---|
| Nodes / edges | 385 / 715 | 3,073 / 6,007 |
| Nodes that are prose (document, concept, rationale) | 80% | 31% |
| Nodes that come from test files | 12% | 54% |
| God nodes | the three `SKILL.md` files, the v1.6 letter spec, `evidence-rules.md` | `run_guards()`, `entry()`, `Page`, `parse_sheet()`, `/apply command` |
| Concept nodes mentioning fabricate / invent / grounding | 23 | 7 |
| Concept nodes mentioning trust / untrusted / injection / hidden | 6 | 12 |
| Concept nodes mentioning page limit / trim / cut | 11 | 31 |
| Concept nodes mentioning hook / anecdote / narrative | 7 | 4 |
| Concept nodes mentioning language / translation | 0 | 19 |
| Concept nodes mentioning tracker / outcome / archive | 0 | 36 |
| Concept nodes mentioning scrape / portal / search | 3 | 116 |

What this says, in plain terms:

- **This plugin is a document; the other repo is a codebase.** Four out of five nodes here are
  prose concepts, and the hubs are the skill files and the evidence rules. Over half of
  ai-job-search's graph is test code, and its hubs are Python functions (the CI security
  guard, the salary parser, the layout verifier). That is why its guarantees are mechanical
  and this plugin's are instructional, which is the root of findings 1.8 and 1.9 above.
- **The anti-fabrication idea is three times denser here.** 23 concept nodes against 7. The
  graph's own hyperedges confirm it: "Three skills sharing one evidence engine" and
  "Non-fabrication guardrails across resume, harvest and letter" are the two strongest group
  relationships in this repo. Nothing equivalent exists in the other graph; its grounding
  audit is one concept inside `/apply`.
- **The letter craft is deeper here, the page mechanics deeper there.** Hook, anecdote and
  narrative appear 7 times here versus 4 there; page-limit and trimming concepts appear 31
  times there versus 11 here, and five of the other graph's "surprising connections" all
  point at `verify_pdf()` from the apply command, the CV template and CI. The other repo has
  spent its effort on the PDF; this one on the sentence.
- **Whole topics are absent here by design.** Language handling, application tracking,
  interview prep and portal search have zero or near-zero nodes in this graph. Only language
  handling (finding 1.4) is a gap for a CV and letter tool; the rest is scope the plugin
  chose not to have.
- **Shared concepts the merge found.** Writing guide, letter structure, company research,
  the page-limit-and-trim rule, the "untrusted input" rule, and the letter finalisation
  checklist each exist in both graphs under different names. These are the places where
  the two projects solved the same problem independently, and where the comparison table
  in section 2 draws its "same" rows.

Outputs: `graphify-out/graph.html` (this repo), the ai-job-search clone's
`graphify-out/graph.html` in the session scratchpad, and
`graphify-out/cross-repo-graph.json` for a cross-repo query. `graphify-out/` is untracked
and shows in `git status`; add it to `.gitignore` or commit only the outputs worth sharing.
