# Resume Optimizer

Tailor your resume to any job description without fabricating a word — a Claude Code skill.

Give it your resume (PDF, DOCX, Markdown, or plain text) and a job description (file, pasted text, or URL). It returns a role-tailored resume in clean markdown — plus an optional ATS-friendly PDF — after running a strict factual validation pass: nothing appears in the output that you didn't actually claim.

## What it does

1. Extracts a factual record from your resume.
2. Analyzes the job description (requirements, keywords, what the employer values).
3. Classifies every requirement: strongly supported / partially supported / not demonstrated / unknown.
4. Rewrites the resume to lead with your strongest *supported* evidence.
5. Validates every claim in the output against your original input.

You get five sections back: a job match analysis, the optimized resume, a list of changes made, targeted questions that could strengthen the application, and an explicit factual-validation report.

**What it will never do:** invent metrics, add technologies from the job posting that you didn't list, inflate titles or seniority, or turn "contributed to" into "led". A less impressive but fully defensible claim always beats one you can't back up in an interview.

## Install

In Claude Code:

```
/plugin marketplace add KivancSerefoglu/resume-optimizer
/plugin install resume-optimizer@resume-optimizer
```

## Use

Just ask, with your files at hand:

```
Tailor my resume (resume.pdf) to this job posting: https://example.com/jobs/data-engineer
```

or paste the job description directly. The skill asks only for what's missing (e.g., your career level), then produces the five-section output. Approve the result and it writes `optimized-resume.md` and, if you want, exports a PDF.

## Example

See [examples/sample-run.md](examples/sample-run.md) for a fictional before/after with the expected output shape.

## How it's built

A single Claude Code plugin exposing one skill. The skill uses progressive disclosure: [SKILL.md](plugins/resume-optimizer/skills/resume-optimizer/SKILL.md) carries the workflow; detailed rule sets live in [references/](plugins/resume-optimizer/skills/resume-optimizer/references/); the PDF template is a static HTML file rendered via headless Chrome. No dependencies, no build step, no API keys.

## License

[MIT](LICENSE)
