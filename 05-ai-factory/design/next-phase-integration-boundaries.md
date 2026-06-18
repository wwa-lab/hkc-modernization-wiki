# Next-Phase Integration Boundaries

Status: Draft

This document defines future integration boundaries for using this repository as
a preparation layer for the new core system.

This repository is not intended to become a legacy code parser, RPG analysis
engine, or automatic architecture generator. Its purpose is to convert raw
project material and SME knowledge into reviewed, traceable inputs that future
core-system design work can trust.

## Repository Purpose

The repository supports this flow:

```text
raw project materials / SME knowledge
-> prepared discovery notes
-> reviewable candidates
-> SME-confirmed legacy knowledge
-> core-system input package
-> target mapping / SDD draft support
```

It should not drift into this flow:

```text
RPG source
-> parser
-> automatic architecture
```

## Non-Goals

The next phase does not include:

- real LAN folder content ingestion
- real LLM API integration
- RPG source or RPG scan parsing
- BRD parser implementation
- database integration
- Web UI
- direct generation of approved target architecture
- writing unreviewed AI output into final dictionaries or mappings

## Source of Truth

The current source of truth remains:

- intake manifests: `05-ai-factory/intake/*.json`
- prepared candidates: `05-ai-factory/logs/*-candidates.json`
- SME Review Packs: `05-ai-factory/review-packs/*.md`
- reviewed SME packs: `05-ai-factory/reviewed/*.md`
- dictionaries: `03-dictionaries/*.json`
- reports: `06-reports/*.md`
- mapping candidates: `04-mappings/*.json`

## Design Principles

- Keep machine-readable data in JSON.
- Keep SME-facing review material in Markdown.
- Keep the LAN folder as the raw evidence source of truth.
- Store references and prepared notes, not uncontrolled copies of raw documents.
- Do not write unreviewed AI output into final dictionaries or mappings.
- Every candidate item must be traceable to source material IDs or prepared note IDs.
- Every dictionary update must be based on an SME-reviewed decision.
- Future scripts must remain runnable on Windows with `py -3`.
- Use Python standard library first unless a later approved design changes that
  constraint.

## Boundary 1: Source Material Registry

Purpose:

Record where raw source materials live and assign stable IDs that can be cited
by prepared notes, candidates, dictionaries, and reports.

This is a metadata boundary, not a content ingestion boundary.

Inputs:

- intake JSON
- approved LAN folder reference
- material owner
- material purpose
- material type

Outputs:

```text
07-references/source-document-index.json
06-reports/latest-intake-report.md
```

Example source material record:

```json
{
  "material_id": "MAT-...",
  "intake_id": "HKC-INTAKE-...",
  "source_path": "\\\\LAN\\HKC\\...",
  "material_type": "meeting_notes|legacy_scan_summary|business_note|field_list",
  "owner": "SME|Tech|BA",
  "purpose": "Explain legacy order entry behavior.",
  "registered_at": "YYYY-MM-DD",
  "content_status": "Referenced Only"
}
```

Rules:

- Do not copy raw LAN content into this repository.
- Do not parse source code or full BRDs at this boundary.
- Every downstream candidate should cite `material_id` values where possible.

Possible future script:

```text
05-ai-factory/scripts/register_source_materials.py
```

## Boundary 2: Prepared Discovery Notes

Purpose:

Capture human-prepared or lightly agent-assisted notes that summarize relevant
legacy knowledge in a form suitable for candidate generation.

Prepared notes can come from:

- SME interviews
- BA discovery notes
- manually summarized LAN documents
- tool-exported summaries
- Copilot-assisted notes reviewed by a human

Inputs:

- source material IDs
- note author
- note date
- legacy topic
- prepared note text

Outputs:

```text
05-ai-factory/prepared-notes/*.md
```

Recommended note shape:

```markdown
# Prepared Note: Order Entry Overview

- Note ID: NOTE-...
- Intake ID: HKC-INTAKE-...
- Source Material References: MAT-..., MAT-...
- Prepared By: ...
- Prepared Date: YYYY-MM-DD
- Review Status: Draft

## Legacy Facts

- ORDENTR is used by users to create customer orders.
- CUSTNO is used on order records.

## Open Questions

- Is CUSTNO bill-to or ship-to in this specific file?
```

Rules:

- Prepared notes are not final truth.
- Prepared notes may feed candidate generation.
- Prepared notes must preserve source references.
- Prepared notes must not bypass SME review.

## Boundary 3: Candidate Generation

Purpose:

Convert prepared notes into structured, reviewable candidate items.

Candidate generation may be manual, script-assisted, or LLM-assisted later, but
the output contract remains the same.

Inputs:

- intake ID
- prepared notes
- source material index
- optional prompt or extraction version

Output:

```text
05-ai-factory/logs/<intake_id>-candidates.json
```

Candidate item contract:

```json
{
  "item_id": "SME-ITEM-...",
  "type": "Program Review|Field Review|File Review|Job Review",
  "legacy_object": "ORDENTR",
  "ai_recommended_answer": "...",
  "why_ai_recommends_this": "...",
  "evidence": ["..."],
  "confidence": "Low|Medium|High",
  "alternative_answers": ["..."],
  "question_for_sme": "...",
  "options": {
    "A": "Accept AI Recommended Answer",
    "B": "Choose Alternative Answer",
    "C": "Provide Corrected Answer",
    "D": "Need Discussion",
    "E": "Not Applicable / Not Correct"
  },
  "source_material_ids": ["MAT-..."],
  "prepared_note_ids": ["NOTE-..."],
  "review_status": "Pending Review"
}
```

Rules:

- Candidate generation may suggest meaning, not approve meaning.
- Weak evidence must produce low confidence.
- Candidate items must remain SME-reviewable.
- Candidate generation must not create target architecture.

Current script:

```text
05-ai-factory/scripts/process_intake.py
```

Possible future script:

```text
05-ai-factory/scripts/generate_candidates_from_notes.py
```

## Boundary 4: SME Review and Decision Capture

Purpose:

Turn uncertain candidate knowledge into reviewed decisions.

Supported review channels:

- GitHub Copilot Chat guided review
- local terminal review through `review_candidates.py`
- manually edited reviewed Markdown

Inputs:

- candidates JSON
- SME Review Pack Markdown
- SME answers

Outputs:

```text
05-ai-factory/reviewed/*.md
06-reports/latest-open-question-report.md
06-reports/latest-review-status-report.md
```

Rules:

- The SME reviews legacy business meaning only.
- The SME should not need to understand Git, JSON, YAML, APIs, Java services,
  target architecture, or domain models.
- Reviewed Markdown is the handoff artifact between SME review and repository
  updates.

Apply rules:

- A writes the AI recommended answer to the relevant dictionary.
- B writes the selected alternative answer to the relevant dictionary.
- C writes the SME corrected answer to the relevant dictionary.
- D writes an open question and does not update dictionaries.
- E writes the review log and does not update dictionaries.

Current scripts:

```text
05-ai-factory/scripts/generate_review_pack.py
05-ai-factory/scripts/review_candidates.py
05-ai-factory/scripts/apply_reviewed_pack.py
```

## Boundary 5: Legacy Knowledge Dictionaries

Purpose:

Store SME-confirmed legacy knowledge as machine-readable input for future core
system work.

Outputs:

```text
03-dictionaries/legacy-programs.json
03-dictionaries/legacy-files.json
03-dictionaries/legacy-fields.json
03-dictionaries/legacy-jobs.json
```

Rules:

- Dictionary entries must be based on reviewed Markdown.
- Dictionary entries must preserve source references.
- Dictionary entries should include `review_source`, `intake_id`, and
  `last_updated`.
- `Need Discussion` and `Not Applicable / Not Correct` items must not be written
  to dictionaries.

## Boundary 6: Core-System Input Package

Purpose:

Package reviewed legacy knowledge into a form that new core-system design teams
can consume.

This is the key next-phase output of this repository.

Possible package contents:

- confirmed legacy program meanings
- confirmed legacy field meanings
- confirmed legacy file meanings
- unresolved business questions
- migration assumptions
- evidence references
- candidate business capability areas
- candidate data concept areas
- review status summary

Possible output location:

```text
06-reports/core-system-input-package.md
06-reports/core-system-input-package.json
```

Rules:

- The package is an input to core-system review, not an approved design.
- The package must separate confirmed knowledge from open questions.
- The package must keep source traceability.
- The package must not invent target services, APIs, or data models without
  technical review.

Possible future script:

```text
05-ai-factory/scripts/generate_core_input_package.py
```

## Boundary 7: Target Mapping and SDD Draft Support

Purpose:

Support later target mapping and draft SDD work after enough reviewed knowledge
exists.

Inputs:

- confirmed dictionaries
- core-system input package
- open question report
- target design constraints, when available

Outputs:

```text
04-mappings/legacy-program-to-target-service.json
04-mappings/legacy-file-to-target-table.json
04-mappings/legacy-field-to-target-field.json
```

Rules:

- Mapping candidates depend on confirmed dictionary entries.
- Mapping candidates are not approved architecture.
- Mapping candidates require core-system review or technical review.
- SDD drafts must preserve unresolved questions and assumptions.

Possible future scripts:

```text
05-ai-factory/scripts/generate_mapping_candidates.py
05-ai-factory/scripts/generate_sdd_draft.py
```

## Review Gates

Recommended status progression:

```text
Referenced Only
-> Prepared Note Draft
-> Candidate Generated
-> Pending SME Review
-> SME Confirmed | Need Discussion | Not Applicable / Not Correct
-> Core-System Input Candidate
-> Core Review
-> Mapping Candidate
-> SDD Draft
```

Rules:

- `Pending Review` items cannot be written as `SME Confirmed`.
- `Need Discussion` items cannot be written to final dictionaries.
- `Not Applicable / Not Correct` items cannot be written to final dictionaries.
- Core-system input packages must distinguish confirmed knowledge from open
  questions.
- Mapping candidates cannot be treated as approved target architecture.

## Validation Extensions

Future validation should check:

- every candidate `source_material_ids` value exists in
  `source-document-index.json`
- every candidate `prepared_note_ids` value exists in prepared notes
- every dictionary item references a reviewed pack
- every core-system input package item references confirmed dictionaries or open
  questions
- every mapping candidate references confirmed dictionary item IDs
- generated reports exist and are non-empty

## Recommended Next Implementation Order

1. Add prepared-notes conventions and sample prepared notes.
2. Add metadata-only source material registration.
3. Add candidate generation from prepared notes.
4. Add core-system input package generation.
5. Add core review checklist for input packages.
6. Add mapping candidate support after enough reviewed knowledge exists.

Each step should include sample data, dry-run behavior when writing outputs,
backup behavior where needed, and validation coverage before moving to the next
step.
