# Humanizer Pass

Shared by every skill that drafts a document. It runs the user's installed `humanizer`
skill over a finished draft so the page does not read as AI-written, without moving a
single fact. The résumé skill calls it at Step 5b and the cover-letter skill inside
Step 5, in both cases before the reviewer, so the reviewer and the validation step read
the humanized wording.

## When to skip

- **Not installed.** If `humanizer:humanizer` is not in this session's skill list, skip
  the pass. Report `skipped: humanizer not installed` and, once per run, suggest
  installing the humanizer plugin.
- **Not English.** The humanizer's patterns describe English prose. For a draft in any
  other language, skip the pass and report `skipped: <language> draft`.

Skipping changes nothing else in the run.

## How to call

Invoke `humanizer:humanizer` with the Skill tool in its embedded mode, so it returns the
final text only. Pass the draft (the résumé as its markdown, the letter as plain text),
followed by [Guardrails for every document](#guardrails-for-every-document) and the
guardrails for this document type, stated as overriding the humanizer's own rules where
they differ. Keep only the final text it returns. Never paste its draft, its audit
bullets or its summary into the document.

## Guardrails for every document

- Keep verbatim: every name, employer, job title, degree, date, number, technology and
  URL. Approximate figures keep their exact wording: "roughly halving" stays "roughly
  halving", never "about half" or "50%".
- Add no fact, metric, tool or claim. This is already the humanizer's own rule, and
  [evidence-rules.md](evidence-rules.md) still governs every claim on the page.
- Keep the section headings and their order.

## Résumé guardrails

- Bullets stay action-verb lines with no subject ("Built …"). Never add "I".
- Keep every `**bold**` marker on exactly the words it wraps.
- Keep the en dash in date ranges (`Jun 2024 – Present`). Remove dashes only elsewhere.
- Neutral register: no personality, opinion or first person.
- Add, drop, merge or split no bullet. Structure belongs to Steps 4 and 5 and to the
  page limit, not to this pass.

## Letter guardrails

- Voice is welcome, in the register the cover-letter skill's Choices Made names.
- Where the humanizer and the cover-letter skill's voice reference (`letter-voice.md`)
  disagree, the voice reference wins.
- Leave the salutation, the closing and the signature exactly as drafted.

## After it returns

1. Compare the result with the draft you passed in.
2. Revert any edit that changes a protected item above, removes a date-range dash,
   moves, drops or adds a bold marker, or adds a claim the draft did not make.
3. Résumé: recount bold against the budget, at most two per bullet and ten per page.
4. Count the edits kept and the edits reverted.

## What to report

- **Factual Validation:** one line, `**Humanizer:** ran (N edits kept, M reverted)`, or
  `**Humanizer:** skipped: humanizer not installed`, or
  `**Humanizer:** skipped: <language> draft`.
- **Changes Made** (résumé) or **Choices Made** (letter): a one-line summary of what the
  pass changed, then each reverted edit with the guardrail it broke.
