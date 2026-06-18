# Core-System Input Preparation Guideline

Status: Draft

This guideline explains how to use this repository to prepare reviewed inputs
for the future core system.

## Repository Role

This repository is a decision-preparation and knowledge-control layer.

It should help the team:

- collect references to raw project materials
- prepare lightweight discovery notes
- generate reviewable candidate knowledge
- capture SME decisions
- maintain confirmed legacy dictionaries
- package reviewed knowledge for core-system design review

It should not become:

- a raw LAN folder mirror
- an RPG parser
- a BRD parser
- a replacement for SME review
- an automatic target architecture generator
- a source of unreviewed target mappings

## Working Model

Use this repository to move information through five controlled states:

```text
Referenced
-> Prepared
-> Candidate
-> SME Reviewed
-> Core-System Input
```

Each state should have a clear artifact:

- Referenced: `07-references/source-document-index.json`
- Prepared: `05-ai-factory/prepared-notes/*.md`
- Candidate: `05-ai-factory/logs/*-candidates.json`
- SME Reviewed: `05-ai-factory/reviewed/*.md`
- Core-System Input: `06-reports/core-system-input-package.*`

## Manual vs Agent Work

Manual work:

- identify source materials
- prepare or approve discovery notes
- answer SME review questions
- decide whether open questions are resolved
- review core-system input packages

Agent-assisted work:

- normalize intake data
- generate candidate review items
- generate Markdown SME Review Packs
- run terminal review flow
- apply reviewed Markdown into dictionaries and reports
- validate repository artifacts
- generate draft input packages for review

Agent output must remain reviewable and traceable.

## Prepared Notes Guideline

Prepared notes are the preferred bridge between raw materials and reviewable
candidates.

Good prepared notes:

- cite source material IDs
- use legacy business language
- separate facts from assumptions
- list open questions explicitly
- avoid target architecture claims

Avoid:

- dumping full raw documents into the repo
- copying large BRD sections
- adding source code excerpts unless explicitly approved
- claiming final truth before SME review

## Candidate Guideline

Candidate items should be small and answerable.

Each candidate should ask one SME-reviewable question, such as:

- What is this legacy program used for?
- What does this legacy field mean?
- Is this file a business file or temporary work file?
- Is this item not applicable for the new core-system knowledge base?

Do not ask SMEs to review:

- target service names
- Java classes
- API paths
- database table design
- architecture decomposition

## SME Review Guideline

SME review should stay in legacy language.

Use the A/B/C/D/E model:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Only A, B, and C can produce dictionary updates.

D must create open questions.

E must create review log entries and stay out of dictionaries.

## Dictionary Guideline

Dictionaries store confirmed legacy knowledge.

Dictionary entries should include:

- stable legacy object ID
- description or meaning
- source evidence
- source material IDs
- reviewed pack source
- SME selected option
- review status
- last updated date

Do not write unreviewed candidate content to dictionaries.

## Core-System Input Package Guideline

Core-system input packages should help future design teams understand what has
been confirmed and what remains unresolved.

Recommended package sections:

- scope and intake ID
- confirmed legacy concepts
- confirmed fields and files
- known process or program responsibilities
- unresolved questions
- migration assumptions
- evidence references
- candidate capability areas
- candidate data concept areas
- review status summary

The package should not present target mappings or SDD content as approved.

## Quality Gates

Before a package is used for core-system review:

- `validate_repo.py` must pass
- all included dictionary entries must be SME confirmed
- all open questions must be listed separately
- every included item must cite reviewed source
- assumptions must be labeled as assumptions
- generated content must be reviewed by a human

## Naming Guidance

Use stable IDs:

- `MAT-...` for source materials
- `NOTE-...` for prepared notes
- `SME-ITEM-...` for review candidates
- `MAP-...` for mapping candidates

Use repository paths consistently:

- source references in `07-references/`
- review artifacts in `05-ai-factory/`
- confirmed dictionaries in `03-dictionaries/`
- reports and packages in `06-reports/`
- mapping candidates in `04-mappings/`
