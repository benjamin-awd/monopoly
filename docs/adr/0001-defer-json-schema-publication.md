---
status: accepted
date: 2026-09-05
supersedes:
superseded-by:
---

# 0001. Defer publishing JSON Schema files; keep models + golden snapshots as the contract

## Context

The `--format json` output is a versioned envelope built by
`src/monopoly/serialize.py`. Its contract is currently enforced two ways: the
Pydantic dataclasses (`Transaction` is a `pydantic_dataclass`,
`transaction.py:64`) and committed golden `expected.json` snapshots that the
bank integration tests assert byte-for-byte.

The envelope carries a single integer `SCHEMA_VERSION` (`serialize.py:26`) that
bumps **only on a breaking change**; additive optional fields do not bump it and
consumers are expected to ignore unrecognised fields (tolerant reader). Additive
fields are expected to be common — `period_start`, account last-4, and FX
amount/currency are known follow-ups — while breaking changes are rare.

The open question: should we also publish a formal, machine-readable JSON Schema,
one file per breaking version (e.g. `schema/v2.json`)? A schema would give
external consumers something to validate and codegen against, which neither the
Python models nor example snapshots provide across languages.

## Decision

**Do not publish a JSON Schema now.** Keep the Pydantic dataclasses plus the
golden `expected.json` snapshots as the contract.

Commit in advance to publishing one — **generated from Pydantic, one file per
breaking `SCHEMA_VERSION`** — as soon as any of these becomes true:

1. a first external/third-party consumer parses the JSON, or we document it as a
   stable public API surface;
2. a non-Python consumer needs to validate or codegen the output;
3. we add a CLI `--validate`/schema-export feature, or a user requests a
   machine-readable contract.

When triggered, the schema is **generated**, not hand-written: introduce a single
`StatementEnvelope` Pydantic model that is the actual source of the serialized
dict, emit `schema/v2.json` via `model_json_schema()` (Draft 2020-12) in CI, and
golden-guard the generated file (the same pattern already used for the CSV
byte-identity test). Leave `additionalProperties` omitted (do not set
`extra="forbid"`) so additive fields stay tolerant and never force a new file or
a version bump. A new schema file is created only on a `SCHEMA_VERSION` bump.

## Alternatives considered

- **Hand-write a JSON Schema per version now.** Rejected: it becomes a third
  source of truth (dataclasses + `serialize.py` + schema) to keep in sync, and
  maximises drift for a contract the models already encode.

- **Generate from the existing Pydantic models now.** Rejected as not currently
  faithful: the published envelope is a hand-assembled dict in `statement_to_dict`
  that reshapes fields — `Transaction.date` → `"transaction_date"`, drops
  `kind`, and lifts balance rows into a separate top-level `balances` list
  (`serialize.py:107`, `:118-127`). `Transaction` has a schema, but there is no
  Pydantic model for the *envelope* (`schema_version`, `bank`, `balances[]`,
  `transactions[]`, `payment_summary`), so `model_json_schema()` would not
  describe what we ship. Faithful generation first requires an envelope model —
  hence that step is folded into the trigger, not done speculatively.

- **A different IDL (TypeSpec, Protobuf/JSON, CUE, Avro).** Rejected: those win
  only when there is already a non-JSON source of truth or a need for wire
  efficiency/codegen. We have neither; JSON Schema is the right tool for a JSON
  document contract when one is eventually needed.

- **Strict, frozen schema per version (`additionalProperties: false`, à la SARIF
  / CycloneDX).** Rejected as contrary to our versioning rule: it turns every
  additive field into a validation failure for older readers, directly violating
  the tolerant-reader / no-bump-on-additive contract we already committed to.

## Consequences

- **Easier now:** no new artifact to maintain; the models and golden snapshots
  already catch structural regressions (field renames, type changes, moves) in
  CI, at zero extra cost.

- **What we give up (the permanent cost):** golden snapshots are a good
  *regression guard* but a poor *contract*. They do not express optionality/
  nullability rules, enum domains (e.g. `direction ∈ {credit, debit}`), value
  formats (ISO-8601 dates, sha256 ids), or cardinality, and they give external
  consumers nothing machine-readable to validate against. Until a schema is
  published, any non-Python consumer must reverse-engineer the shape from
  examples. This gap is deliberate and only bites once the trigger conditions
  above are met — at which point this decision is revisited (superseding ADR).
