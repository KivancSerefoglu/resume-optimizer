# Resume Optimizer

A Claude Code plugin that helps you apply to jobs faster — without lying on your resume.

It does three things:

1. **Tells you if a job is worth applying to** (before you waste an evening on it)
2. **Tailors your resume** to a specific job posting
3. **Writes a cover letter** to go with it

Everything it writes only uses facts you actually gave it. It will never invent a metric, a skill, or a feeling you didn't mention — it just picks the truest, most relevant parts of your background and presents them well.

## Who this is for

Anyone tired of manually rewriting their resume for every single job application. You give it your background once, and from then on, tailoring a resume or writing a cover letter for a new job takes one message instead of an hour.

## Before you start

You need [Claude Code](https://claude.com/claude-code) installed and running. That's it — no accounts, no API keys, no extra setup.

## Step 1: Install the plugin

Open Claude Code and paste these two lines:

```
/plugin marketplace add KivancSerefoglu/resume-optimizer
/plugin install resume-optimizer@resume-optimizer
```

That's the whole installation.

## Step 2: Give it something to work with

You need one of these two things:

- **An existing resume** (a PDF or doc), OR
- **A `background.md` file** — a plain text file listing everything you've done: jobs, projects, numbers, courses. (Recommended if you're job-hunting seriously — see below.)

If you only have a resume, that's fine to start. The first time you use it, it will offer to turn your resume into a reusable `background.md` file automatically, so future applications are faster.

## Step 3: Use it

Everything below is a message you type directly into Claude Code, in plain English. Just swap in your own file and job link.

### "Should I even apply?"

```
How well do I match this job posting? background.md — https://example.com/jobs/data-engineer
```

You'll get a percentage match, a table showing exactly why, and a clear verdict: **Apply**, **Apply with caveats**, or **Skip**. Nothing gets saved to your computer — this is just a gut check.

### "Tailor my resume to this job"

```
Tailor my resume (resume.pdf) to this job posting: https://example.com/jobs/data-engineer
```

or, once you have a `background.md` file:

```
Generate a CV from background.md for this job posting: https://example.com/jobs/data-engineer
```

You get back:
- A match score and why
- A tailored resume, as both `optimized-resume.md` and a ready-to-send `optimized-resume.pdf` (one page)
- A plain list of what it changed and why
- A few questions that could make your application even stronger

**Tip:** If you have a GitHub profile, add it to the message and it will pull your real projects from your repos automatically:

```
Generate a CV from background.md for https://example.com/jobs/data-engineer — also use my projects at github.com/myusername
```

### "Write me a cover letter"

```
Write a cover letter for this posting: https://example.com/jobs/data-engineer — background.md
```

It writes a one-page cover letter (`cover-letter.md` and `cover-letter.pdf`) that opens with something true and specific about you — not a generic "I am excited to apply" line — and ties it to why you fit the role. If it needs a personal detail it doesn't have yet, it will just ask you.

## What it will never do

- Make up a number, metric, or result you didn't provide
- Add a skill or technology from the job posting that you never mentioned
- Upgrade your job title or turn "helped with" into "led"
- Invent a feeling or story for the cover letter's opening line

If something isn't strong enough to say honestly, it leaves it out rather than stretching it. A believable resume beats an impressive one you can't defend in an interview.

## Want to see it in action first?

Check [examples/sample-run.md](examples/sample-run.md) for full example runs, showing exactly what the input looks like and what you get back.

## How it works, briefly

One plugin, three skills (`match-analysis`, `resume-optimizer`, `cover-letter`) that all share the same fact-checking engine, so a claim that's rejected in one is rejected in all three. No dependencies to install, no build step, no API keys — it runs entirely inside Claude Code.

## License

[MIT](LICENSE)
