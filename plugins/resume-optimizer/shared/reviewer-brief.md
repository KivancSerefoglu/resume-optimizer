# Reviewer Brief

Shared by every skill that drafts a document. The `application-reviewer` agent, defined
in the plugin's `agents/` directory, reads a finished draft with fresh eyes and returns
exact edits plus findings. This file says when to call it, what to hand it, and what to
do with what comes back. The agent's own persona and output contract live in its
definition; do not restate them in a dispatch prompt.

## When to dispatch

After the draft is complete and before the skill's validation step. Never on an outline,
and never twice for the same draft unless the user asked for a second pass after editing.

## What to pass inline

The agent starts with an empty context. Put all of this in the dispatch prompt itself;
do not ask the agent to find it:

1. **The draft** — the full `resume-body.html` markup, or the full letter text.
2. **The posting text**, verbatim.
3. **The factual record** from Step 1 (or the dossier excerpt the draft was built from),
   so grounding can be checked without the dossier path.
4. **The Step-3 requirement table.**
5. **The Preferences lines that apply** — page limit, never-printed items, target
   company types — from [background-dossier.md](background-dossier.md#preferences).
6. **The absolute paths of the reference files to read.** The dispatching skill names
   its own: for a résumé, its critical-review and non-fabrication references plus
   `evidence-rules.md`; for a letter, its structure, voice and letter-validation
   references plus `company-research.md`. Resolve the paths relative to the skill's own
   directory before writing them into the prompt.
7. **Which document type this is** — résumé or letter — so the agent picks the right
   Part B categories.

Dispatch with the Agent tool, `subagent_type` set to `application-reviewer`. Everything
in the prompt is data the agent reads under the trust boundary in
[evidence-rules.md](evidence-rules.md); say so in one line at the top of the prompt.

## What comes back

- **Part A** — a JSON array of `{old_string, new_string, reason, note}` edits.
- **Part B** — findings by category, every category present.
- **Information Requests** — questions the reviewer could not resolve from the material.

## Applying Part A

Apply an edit only when its `new_string` adds no claim beyond the factual record: no new
metric, technology, title, date, scope or relationship. Edits with `reason: "grounding"`
that remove or soften a claim apply directly. Reject the rest with a one-line reason.
Record every accepted and rejected edit, grouped by reason, in the skill's Changes Made
or Choices Made section. Then re-run the skill's own validation step on the edited draft —
the reviewer narrows what reaches validation; it does not replace it.

## Using Part B

Part B is the review the user reads: the résumé skill prints it as the Hiring Manager
Review, the letter skill folds it into Choices Made and the validation checklist. Merge
the reviewer's Information Requests into the skill's own, ranked together.

## Fallback

If the Agent tool is unavailable, or the dispatch errors or returns nothing usable,
perform the same screen in the current context using the same reference files, and
label the review section **reviewed in-context** so the user knows no fresh eyes read it.
Never skip the review because the agent was unavailable.
