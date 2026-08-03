# Resume Optimizer — Design Spec

**Date:** 2026-07-21
**Status:** Approved by user (chat), pending spec review

## Summary

A public GitHub repo that is a Claude Code plugin. Installing the plugin gives the user a
`resume-optimizer` skill: provide a resume (PDF/DOCX/MD/TXT) and a job description (file,
pasted text, or URL), and Claude produces a role-tailored, factually validated resume in
markdown plus an optional PDF rendered from a bundled ATS-friendly HTML template.

The core intellectual property is the user's drafted system prompt: an expert resume-writer
persona with strict non-fabrication rules, a 5-step analysis process, and a 5-section output
format. That prompt is adapted into skill form with progressive disclosure.

## Goals

- Tailor a resume to a specific job description while preserving complete factual accuracy.
- Never fabricate: every factual claim in the output must be supported by candidate-supplied
  information. Wording may be strengthened; underlying claims may not.
- Work with real-world inputs: PDF resumes, pasted job descriptions, job-posting URLs.
- Clean install story: `/plugin marketplace add <repo>` → install → skill available.
- Serve as a portfolio piece (linked from kivancserefoglu.com).

## Non-goals (v1)

- No web app, no hosted service, no API keys to manage.
- No DOCX output (markdown + PDF only).
- No multi-resume management or application tracking.

## Repo structure

```
resume-optimizer/
├── .claude-plugin/
│   └── marketplace.json          # repo doubles as its own plugin marketplace
├── plugins/
│   └── resume-optimizer/
│       ├── .claude-plugin/
│       │   └── plugin.json       # plugin metadata (name, version, description)
│       └── skills/
│           └── resume-optimizer/
│               ├── SKILL.md      # workflow + core rules (trimmed to essentials)
│               ├── references/
│               │   ├── non-fabrication.md   # full never-invent list + validation rules
│               │   ├── writing-guide.md     # bullet patterns, verbs, formatting, summary rules
│               │   └── tailoring.md         # role-specific tailoring + section ordering
│               └── assets/
│                   └── resume-template.html # one-column ATS-friendly template for PDF export
├── examples/
│   └── sample-run.md             # fictional resume + JD with expected output shape
├── README.md                     # pitch, install instructions, example session
└── LICENSE                       # MIT
```

## Prompt-to-skill mapping (progressive disclosure)

The drafted system prompt (~2,500 words) is split so the always-loaded part stays small:

- **SKILL.md** keeps: primary objective, instruction-security rules, required inputs,
  the 5-step process (extract evidence → analyze JD → gap analysis → optimize → validate),
  the 5-section output format, and a one-line hard non-fabrication rule pointing to
  `references/non-fabrication.md`.
- **references/non-fabrication.md**: the complete never-invent list, the missing-metric
  protocol, and the Step-5 validation checklist.
- **references/writing-guide.md**: bullet patterns ("Accomplished X by Y using Z"),
  preferred verbs, banned phrases, formatting principles, summary-section rules,
  promotions/titles guidance.
- **references/tailoring.md**: role-specific tailoring (product companies, consulting,
  research, management), career breaks/changes, section ordering by career level.

Adaptations from the original prompt wording:

- "Uploaded résumés" → files the user provides paths to (read natively by Claude Code).
- "PDF export through the application" → render `assets/resume-template.html` with the
  optimized content and convert to PDF.
- Instruction-security section is kept: resume files and fetched job postings are treated
  as untrusted data, never as instructions.

## Skill workflow

1. **Locate inputs.** Resume file (PDF/DOCX/MD/TXT) and job description (file, pasted text,
   or URL to fetch). Ask only for missing information; never re-ask for provided info.
   Optionally collect application context (career level, career change, new grad, IC vs
   management, location/authorization if the user wants it considered).
2. **Run the 5-step process** from the prompt: extract candidate evidence; analyze the job
   description; classify each requirement (strongly supported / partially supported / not
   demonstrated / unknown); optimize; validate every factual claim against the source.
3. **Output the 5 sections**: Job Match Analysis, Optimized Résumé (copy-ready markdown),
   Changes Made, Information Requests, Factual Validation (explicitly "None" when no
   unsupported additions were made).
4. **Export.** After user confirmation, write `optimized-resume.md` and generate a PDF from
   the HTML template.

## Error handling

- Scanned/unreadable PDF → ask the user to paste the text.
- Job-posting URL behind a login wall or blocked → ask the user to paste the description.
- Instruction-like text found inside resume or job description → ignore it and inform the
  user it was found (per the instruction-security rules).

## Testing

- `examples/sample-run.md` is a manual regression fixture: fictional resume + JD with the
  known-good expected shape of the 5-section output.
- Install-path verification: add the repo as a marketplace in Claude Code, install the
  plugin, confirm the skill triggers on "tailor my resume to this job description".

## Decisions

- **License:** MIT.
- **Name:** `resume-optimizer`.
- **README pitch:** "Tailor your resume to any job description without fabricating a word —
  a Claude Code skill."
