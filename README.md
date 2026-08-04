# Resume Optimizer

Tailor your resume — or generate a one-page CV from your full background — for any job description, without fabricating a word. Three Claude Code skills: one scores a posting against your background, one writes the resume, one writes the cover letter.

Two ways to use it, plus an optional shortcut:

- **Dossier mode (recommended):** keep one `background.md` master file with everything you've ever done — every job, project, metric, and course — plus a Narrative section for the story material a resume cannot show. Give the skill that file plus a job posting; it selects the relevant subset and generates a one-page, ATS-friendly CV as markdown **and PDF**.
- **Resume mode:** give it an existing resume and a job description; it tailors the resume.
- **Portfolio links (optional):** add your GitHub profile, specific repos, a portfolio site, or a LinkedIn URL and it reads your projects from there instead of making you describe each one. Harvested projects are merged with your background file — the repo supplies languages, dates, and scale; your file supplies impact and context — and are used for that run only. Nothing is written back to `background.md`.

## What it does

Three skills, sharing one evidence engine.

### `/resume-optimizer:match-analysis` — should I apply?

1. Extracts a factual record from your background file or resume.
2. Analyzes the job description (requirements, keywords, what the employer values).
3. Classifies every requirement and computes a transparent **job-match percentage** — a weighted breakdown table you can audit, never a black-box "ATS score".
4. Returns an **Apply / Apply with caveats / Skip** verdict plus the single gap that would move the score most.

Writes nothing to disk. Run it on a posting before you spend an evening on the application.

### `/resume-optimizer:resume-optimizer` — write the resume

Runs the same three analysis steps, then:

4. Writes the resume to lead with your strongest *supported* evidence.
5. Validates every claim against your input, then writes `optimized-resume.md` and `optimized-resume.pdf` (one page enforced in dossier mode).

**What they will never do:** invent metrics, add technologies from the job posting that you didn't list, inflate titles or seniority, or turn "contributed to" into "led". Leaving things out is fair game — that's tailoring. Changing facts is not. A less impressive but fully defensible claim always beats one you can't back up in an interview.

### `/resume-optimizer:cover-letter` — write the letter

Runs the same analysis silently to pick the two or three things worth writing about, then:

1. Draws a hook from the **Narrative** section of your background file — how you got into
   the field, a project that redirected you, a product you actually use, who referred you.
   It offers a few openings and you pick one. It will not invent an anecdote.
2. Researches the employer from the posting and their own site, and uses only specifics it
   can cite back to you.
3. Writes `cover-letter.md` and `cover-letter.pdf`, one page, on a letterhead matching your
   resume.

Paste in an existing letter instead and it critiques that against the same rules.

**The failure it is built to prevent:** a resume fabricates by inventing a metric; a cover
letter fabricates by inventing a feeling. "I've long admired your work" reads as warmth,
not as a lie — so the skill will not write it unless you said it.

## Install

In Claude Code:

```
/plugin marketplace add KivancSerefoglu/resume-optimizer
/plugin install resume-optimizer@resume-optimizer
```

## Use

### Score a posting

```
How well do I match this job posting? background.md — https://example.com/jobs/data-engineer
```

You get the match percentage, the audit table, the gaps, and an Apply / Apply with caveats / Skip verdict. Nothing is written to disk; if the verdict is positive it offers to hand off to `/resume-optimizer:resume-optimizer`.

### Write the resume

First run (no background file yet):

```
Tailor my resume (resume.pdf) to this job posting: https://example.com/jobs/data-engineer
```

The skill offers to build a reusable `background.md` from your resume plus a few targeted questions. Keep that file — every later application is then just:

```
Generate a CV from background.md for this job posting: https://example.com/jobs/data-engineer
```

Either way you get: a job-match score with its breakdown, the optimized resume, a list of changes, targeted questions that could strengthen the application, a factual-validation report — and `optimized-resume.md` + `optimized-resume.pdf` on disk.

To pull your projects straight from GitHub:

```
Generate a CV from background.md for https://example.com/jobs/data-engineer — also use my projects at github.com/myusername
```

It fetches your repos, picks the ones that fit the role, and describes each one according to what the commit history actually shows — your own projects as yours, contributions to other people's repos as contributions.

### Write the cover letter

```
Write a cover letter for this posting: https://example.com/jobs/data-engineer — background.md
```

It asks what it needs for the hook if your background file has no Narrative section yet,
and offers to save your answers there so the next letter is cheaper.

## Example

See [examples/sample-run.md](examples/sample-run.md) for fictional before/after runs in both modes with the expected output shape.

## How it's built

A single Claude Code plugin exposing three skills: `match-analysis`, `resume-optimizer`, and `cover-letter`. Machinery both need — evidence rules, the background-dossier format, portfolio link harvest, and the scoring rubric — lives in [shared/](plugins/resume-optimizer/shared/), so the rubric has exactly one copy. Each skill's `SKILL.md` carries only its own workflow; resume-specific rule sets live in [references/](plugins/resume-optimizer/skills/resume-optimizer/references/); the PDF templates are static HTML files rendered via headless Chrome, and one shared script derives the markdown from the rendered HTML so the two deliverables cannot drift. No dependencies, no build step, no API keys.

## License

[MIT](LICENSE)
