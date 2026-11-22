# Humanizer Pass

Shared by every skill that drafts a document. It runs the user's installed `humanizer`
skill over a finished draft so the page does not read as AI-written, without moving a
single fact. The résumé skill calls it at Step 5b and the cover-letter skill inside
Step 5, in both cases before the reviewer, so the reviewer and the validation step read
the humanized wording.

## When to skip

- **Not installed.** The humanizer counts as installed when this session's skill list
  has `humanizer:humanizer` (the plugin) or a skill named `humanizer` (the skills-CLI or
  manual install). If neither is listed, skip the pass. Report
  `skipped: humanizer not installed` and, once per run, suggest installing it with
  `npx skills add blader/humanizer --global`.
- **Not English.** The humanizer's patterns describe English prose. For a draft in any
  other language, skip the pass and report `skipped: <language> draft`.

Skipping changes nothing else in the run.

## How to call

Load whichever humanizer skill is listed with the Skill tool. It returns the humanizer's instructions,
not rewritten text: you apply them yourself, in its embedded mode, to the draft (the
résumé as its markdown, the letter as plain text). Where the humanizer's rules and the
guardrails below differ, the guardrails win. Put only the final rewrite into the
document, never its draft rewrite, audit bullets or summary.

## Guardrails for every document

- Keep verbatim: every name, employer, job title, degree, date, number, technology and
  URL. Approximate figures keep their exact wording: "roughly halving" stays "roughly
  halving", never "about half" or "50%".
- Add no fact, metric, tool or claim. This is already the humanizer's own rule, and
  [evidence-rules.md](evidence-rules.md) still governs every claim on the page.
- Cutting promotional wording ("pivotal", "a testament to", "fostering collaboration")
  is the point of the pass, and so is plainer wording for an inflated phrase ("played a
  key role in" → "contributed to"). Cutting a protected item, or a fact from the
  candidate's record, is not.
- Keep the section headings and their order.

## Résumé guardrails

- Rewrite prose only: bullets, the Summary and project descriptions. Leave headings,
  entry lines (school or employer, degree or title, dates, location), the contact line
  and the Skills lines exactly as drafted, separators included.
- Bullets stay action-verb lines with no subject ("Built …"). Never add "I". This
  overrides the humanizer's rule against subjectless fragments.
- A rewritten bullet still follows the résumé writing guide: never open it with a phrase
  the guide lists under Avoid ("Worked on", "Helped with", "Responsible for").
- Keep every `**bold**` marker on exactly the words it wraps.
- Keep the en dash in date ranges (`Jun 2024 – Present`). This overrides the humanizer's
  dash rule (§14) and its final dash scan. Inside the prose you rewrite, cut other dashes
  as it says.
- Neutral register: no personality, opinion or first person.
- Add, drop, merge or split no bullet. Structure belongs to Steps 4 and 5 and to the
  page limit, not to this pass.

## Letter guardrails

- Voice is welcome, in the register the cover-letter skill's Choices Made names.
- Where the humanizer and the cover-letter skill's voice reference (`letter-voice.md`)
  disagree, the voice reference wins.
- Add no emotion, interest, opinion or history the draft did not state. The humanizer's
  "stance is voice, not facts" does not apply here: in a letter an invented feeling is a
  fabrication.
- The conclusion keeps all four of its jobs from the cover-letter skill's structure
  reference (`letter-structure.md`): employability, thanks, an interview request and a
  contact method. The humanizer's rules on generic conclusions, servile tone and
  "let me know" endings do not cut them.
- Leave the salutation, the closing and the signature exactly as drafted.

## After it returns

1. Compare the result with the draft you passed in.
2. Revert any edit that breaks a guardrail above, including one that changes a
   protected item, removes a date-range dash, moves, drops or adds a bold marker,
   touches a line outside the prose this pass may rewrite, merges, splits or drops a
   bullet, adds "I", adds a feeling or a claim the draft did not make, or cuts one of the
   conclusion's jobs. Revert the whole bullet or sentence
   to its wording before the pass, not just the offending words.
3. Résumé: recount bold against the budget, at most two per bullet and ten per page.
4. Count edits by bullet or sentence: each one the pass changed is one edit, kept or
   reverted.

## What to report

- **Factual Validation:** one line, `**Humanizer:** ran (N edits kept, M reverted)`, or
  `**Humanizer:** skipped: humanizer not installed`, or
  `**Humanizer:** skipped: <language> draft`.
- **Changes Made** (résumé) or **Choices Made** (letter): a one-line summary of what the
  pass changed, then each reverted edit with the guardrail it broke.
