# Repository Usage Guide

This repository is `hkc-modernization-wiki`, a lightweight Agent-readable
knowledge base for HKC modernization discovery.

Use it to maintain Markdown wiki notes, source indexes, dictionaries, mapping
candidates, optional review packs, reviewed results, reports, references, and
decisions.

Do not use it as the raw document repository. The LAN folder remains the source
of truth for raw source documents and project evidence.

## Default Use

- Store wiki and report content as Markdown.
- Store metadata, dictionaries, and indexes as JSON.
- Keep LAN-folder references in source indexes.
- Run Auto Wiki Intake as the default MVP workflow.
- Use SME Review Packs only as optional selective review.

## Default Workflow

```text
Materials/LAN references/inbox files
-> Agent intake
-> Auto classification
-> Wiki update
-> Source index update
-> Open questions/conflict log
-> Intake summary
-> Optional SME review only when needed
```

## Optional SME Review Triggers

Use SME review only for:

- low-confidence items
- conflicts
- critical programs
- key business fields
- important open questions

## Status Rule

Default AI wiki output is `AI Organized`.

Only explicit SME confirmation can produce `SME Confirmed`.

## Windows Commands

Python command examples must use `py -3`.

Example:

```powershell
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-wiki-intake.json
py -3 05-ai-factory\scripts\validate_repo.py
```

The LAN folder remains the source of truth for raw project documents. Do not
copy full BRDs, meeting notes, sign-off files, or raw requirement documents into
this repository.
