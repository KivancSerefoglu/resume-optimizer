# Resume Optimizer

Tailor your resume — or generate a one-page CV from your full background — for any job description, without fabricating a word. A Claude Code skill.

Two ways to use it:

- **Dossier mode (recommended):** keep one `background.md` master file with everything you've ever done — every job, project, metric, and course. Give the skill that file plus a job posting; it selects the relevant subset and generates a one-page, ATS-friendly CV as markdown **and PDF**.
- **Resume mode:** give it an existing resume and a job description; it tailors the resume.

## What it does

1. Extracts a factual record from your background file or resume.
2. Analyzes the job description (requirements, keywords, what the employer values).
3. Classifies every requirement and computes a transparent **job-match percentage** — a weighted breakdown table you can audit, never a black-box "ATS score".
4. Writes the resume to lead with your strongest *supported* evidence.
5. Validates every claim against your input, then writes `optimized-resume.md` and `optimized-resume.pdf` (one page enforced in dossier mode).

**What it will never do:** invent metrics, add technologies from the job posting that you didn't list, inflate titles or seniority, or turn "contributed to" into "led". Leaving things out is fair game — that's tailoring. Changing facts is not. A less impressive but fully defensible claim always beats one you can't back up in an interview.

## Install

In Claude Code:

```
/plugin marketplace add KivancSerefoglu/resume-optimizer
/plugin install resume-optimizer@resume-optimizer
```

## Use

First run (no background file yet):

```
Tailor my resume (resume.pdf) to this job posting: https://example.com/jobs/data-engineer
```

The skill offers to build a reusable `background.md` from your resume plus a few targeted questions. Keep that file — every later application is then just:

```
Generate a CV from background.md for this job posting: https://example.com/jobs/data-engineer
```

Either way you get: a job-match score with its breakdown, the optimized resume, a list of changes, targeted questions that could strengthen the application, a factual-validation report — and `optimized-resume.md` + `optimized-resume.pdf` on disk.

## Example

See [examples/sample-run.md](examples/sample-run.md) for fictional before/after runs in both modes with the expected output shape.

## How it's built

A single Claude Code plugin exposing one skill. The skill uses progressive disclosure: [SKILL.md](plugins/resume-optimizer/skills/resume-optimizer/SKILL.md) carries the workflow; detailed rule sets live in [references/](plugins/resume-optimizer/skills/resume-optimizer/references/); the PDF template is a static HTML file rendered via headless Chrome. No dependencies, no build step, no API keys.

## License

[MIT](LICENSE)
