# hkc-modernization-wiki

HKC Modernization Wiki is a lightweight Agent-readable knowledge base for
modernization discovery.

It is used to organize modernization knowledge from LAN-folder references,
controlled inbox samples, source indexes, Markdown wiki notes, reports, and
optional SME review artifacts.

## What This Repository Is

- A lightweight Agent-readable wiki for HKC modernization discovery.
- A Markdown wiki for AI-organized legacy and modernization notes.
- A JSON metadata workspace for source indexes, dictionaries, and mapping candidates.
- A lightweight local AI factory that uses Python standard library scripts.
- A pilot workspace for Agent conversation over curated modernization knowledge.

## What This Repository Is Not

This repository is not a replacement for the LAN folder.

The LAN folder remains the raw source of truth for BRDs, meeting notes, sign-off
files, exported legacy materials, screenshots, requirements, and original
business or technical evidence.

This repository should reference LAN-folder documents where needed, but it
should not become an uncontrolled copy of the raw document store. Do not copy
full BRDs, raw requirement documents, meeting minutes, sign-off packages, or
other original project materials into this repo.

This MVP does not use Excel, pandas, openpyxl, a database, a Web UI, a real LLM
API, or complex RPG/BRD parsing.

## Main Workflow

The default MVP workflow is Auto Wiki Intake:

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

Auto Wiki Intake writes concise Markdown notes under `03-wiki/`, updates
`07-references/source-document-index.json`, and generates
`06-reports/latest-intake-summary.md`. It also writes an optional SME candidate
log under `05-ai-factory/logs/`; generating a candidate log does not make SME
review part of the default mainline.

## Optional SME Review

SME Review Packs are retained, but they are no longer the default mainline.

Use optional selective SME review only for:

- low-confidence items
- conflicts
- critical programs
- key business fields
- important open questions

SME questions must focus on IBM iSeries, AS400, RPGLE, CLLE, programs, files,
fields, jobs, reports, screens, batch flows, and legacy evidence. Do not ask the
SME to review target architecture, APIs, Java services, domain models, service
decomposition, deployment design, or cloud infrastructure.

## Status Definitions

- `AI Organized` - AI organized or summarized content from source references.
- `Human Touched` - A non-SME human edited or curated the content.
- `SME Corrected` - SME supplied a correction, but final confirmation may still need recording.
- `SME Confirmed` - SME explicitly confirmed, selected, or corrected the item.
- `Need Clarification` - The item needs more context or discussion.
- `Conflict` - Source materials disagree or the meaning is contradictory.
- `Deprecated` - The item is no longer current.

Default AI wiki output is `AI Organized`.

AI-generated content must never be marked `SME Confirmed` unless there is
explicit SME confirmation.

## File Formats

- Markdown: wiki pages, prompts, reports, and optional SME Review Packs.
- JSON: metadata, source indexes, dictionaries, and mapping candidates.
- Python: local scripts using only the standard library.

Windows command examples use `py -3`.

## How To Run

Daily natural-language intake:

```powershell
py -3 05-ai-factory\scripts\process_intake.py --request "处理 HKC wiki inbox，主题是 AP invoice field review"
```

This writes `05-ai-factory\intake\latest-auto-intake.json`, runs Auto Wiki
Intake, updates the wiki, and records the operation.

If the request includes a LAN source path, the script records it as a source
reference without copying the raw document:

```powershell
py -3 05-ai-factory\scripts\process_intake.py --request "把 `\\LAN\HKC\Discovery\AP_Field_List.txt` ingest 到 HKC wiki，主题是 AP fields"
```

Run Auto Wiki Intake from the repository root:

```powershell
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-wiki-intake.json
```

Validate the repository:

```powershell
py -3 05-ai-factory\scripts\validate_repo.py
```

Query the wiki from a natural language question:

```powershell
py -3 05-ai-factory\scripts\query_wiki.py --query "总结 AP invoice 相关知识，列出 source 和 open questions"
```

Optional selective SME review scripts are documented in `05-ai-factory/README.md`.
