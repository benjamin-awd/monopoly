# Architecture Decision Records

This directory records decisions that are **expensive to reverse**, **non-obvious
to a newcomer**, or **likely to be re-litigated** — output schema and format,
extraction strategy, safety-check semantics, how fixtures handle real financial
data, licensing, and dependency choices with lock-in. The code shows *what*; an
ADR preserves *why*, especially the alternatives that were rejected and leave no
trace anywhere else.

Do not write one for a change you would not defend in a PR comment (a one-bank
regex, a behaviour-preserving refactor). If the decision has not been made yet,
it is a plan (`.claude/plans/`), not an ADR.

## Conventions

- One file per decision: `NNNN-kebab-title.md`, `NNNN` zero-padded, one higher
  than the highest existing number (this log starts at `0001`).
- Copy `TEMPLATE.md` to start.
- `status`: `proposed` while still deciding, `accepted` once in effect,
  `deprecated` once superseded.
- Keep it to one page. If it runs longer, it is several decisions — split it.
- **Consequences must include what got harder.** An ADR listing only benefits is
  marketing.

## Superseding

Never edit an accepted ADR's substance. To reverse a decision, write a new ADR,
set its `supersedes:` to the old number, and set the old one's `superseded-by:`
to the new number with `status: deprecated`. Those two frontmatter edits are the
only permitted change to an accepted ADR.

## Index

- [0001](0001-defer-json-schema-publication.md) — Defer publishing JSON Schema
  files; keep models + golden snapshots as the contract (accepted)
