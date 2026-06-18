# GitHub Copilot Instructions

This repository is `hkc-modernization-wiki`, a lightweight Agent-readable
knowledge base for HKC modernization discovery.

The LAN folder remains the source of truth for BRDs, meeting notes, sign-off
files, raw requirements, exported legacy materials, screenshots, and original
project evidence. This repository stores Markdown wiki notes, reports, prompts,
optional review packs, reviewed results, JSON dictionaries, source indexes, and
mapping candidates.

## Default Workflow

Support Auto Wiki Intake as the default path:

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

Default AI wiki output status is `AI Organized`.

Never mark AI-generated content as `SME Confirmed` unless the SME explicitly
accepts it, selects an alternative, or provides a correction.

## Natural Language Intake

Users should not need to hand-write intake JSON for daily work.

When the user asks in natural language to update, ingest, process, or organize
HKC wiki material:

- Convert the request into intake metadata first.
- Save generated metadata to `05-ai-factory/intake/latest-auto-intake.json`.
- Set `submitted_by` to `Agent from user request`.
- Use default status `AI Organized`.
- If the user mentions inbox, scan `05-ai-factory/inbox/`.
- If the user gives a LAN path, record it as a source reference and do not copy
  the raw document.
- If the user gives only a topic and no source path, check the inbox.
- If the inbox is empty and no source path is provided, ask one short question:
  where is the source material?
- After generating intake metadata, run Auto Wiki Intake and validation.

Supported daily phrasing examples:

- `处理 HKC wiki inbox，主题是 invoice matching。`
- `把 \\LAN\\HKC\\Discovery\\AP_Field_List.txt 作为 source reference ingest 到 wiki。`
- `把今天 vendor 给的 AP interface notes 整理进 HKC wiki。`

## Natural Language Wiki Query

When the user asks to summarize, explain, find, list, or compare knowledge that
should already be in the HKC wiki:

- Read `03-wiki/index.md` first.
- Query only `03-wiki/` and `07-references/source-document-index.json`.
- Use `05-ai-factory/scripts/query_wiki.py` when a script answer is useful.
- Include source pages and source material IDs.
- Preserve status and confidence.
- Call out open questions and conflicts.
- If no wiki note exists, say the source has not been ingested yet instead of
  inventing an answer.

Example:

```bat
py -3 05-ai-factory\scripts\query_wiki.py --query "总结 AP invoice 相关知识，列出 source 和 open questions"
```

## Optional SME Review Context

Use optional selective SME review only for low-confidence items, conflicts,
critical programs, key business fields, and important open questions.

The SME may have 20-30 years of IBM iSeries, AS400, RPGLE, and CLLE experience.

Use legacy terms the SME already knows:

- program
- file
- field
- job
- report
- screen
- batch flow
- physical file
- logical file
- RPGLE
- CLLE

Do not ask the SME to review target architecture, APIs, Java services, domain
models, service decomposition, deployment design, or cloud infrastructure.

## Review Style

Ask one item at a time.

For each review item, always show:

- AI Recommended Answer
- Evidence
- Confidence
- A/B/C/D/E options

The SME can answer with `A`, `B`, `C`, `D`, or `E`, or provide a natural
language correction.

If the SME provides a correction, preserve the correction text and convert the
result into the standard reviewed Markdown format.

Use these standard options:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Processing rules:

- A: use the AI Recommended Answer and mark the item as `SME Confirmed`.
- B: use the SME-selected alternative answer and mark the item as `SME Confirmed`.
- C: use the SME Corrected Answer and mark the item as `SME Confirmed`.
- D: do not write to final dictionaries or mappings; mark the item as `Need Clarification`.
- E: do not write to final dictionaries or mappings; mark the item as `Deprecated` or leave it outside dictionaries.

## Output Rules

Generate reviewed Markdown in the standard format used by this repository.

Do not invent evidence. If evidence is incomplete, mark confidence as low and
use optional SME review only when the item matters.

Do not turn SME review into target-solution design. Keep questions focused on
legacy object meaning, usage, source evidence, and modernization relevance.
