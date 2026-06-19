# AI Factory Runbook

This runbook demonstrates the MVP Auto Wiki Intake flow.

For internal testing with real HKC materials, use
`05-ai-factory/design/real-scenario-test-guideline.md`. A Chinese version is
available at `05-ai-factory/design/real-scenario-test-guideline.zh-CN.md`.

The demo is intentionally local and lightweight:

- Python standard library only
- Markdown for wiki pages, prompts, reports, and optional SME review packs
- JSON for metadata, dictionaries, and indexes
- No Excel, pandas, openpyxl, database, Web UI, real LLM API, or real LAN folder read
- No complex RPG or BRD parsing

## Main Workflow

```text
sample-wiki-intake.json
-> process_intake.py
-> auto classification
-> 03-wiki Markdown notes
-> 07-references/source-document-index.json
-> 03-wiki/questions/open-questions.md
-> 03-wiki/questions/conflict-log.md
-> 06-reports/latest-intake-summary.md
```

Windows:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 HKC wiki inbox，主题是 AP invoice field review"
py -3 05-ai-factory\scripts\validate_repo.py
```

The natural language request writes
`05-ai-factory\intake\latest-auto-intake.json` before running intake.

Explicit intake JSON:

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-wiki-intake.json
py -3 05-ai-factory\scripts\validate_repo.py
```

Optional inbox scan:

```bat
py -3 05-ai-factory\scripts\process_intake.py --inbox 05-ai-factory\inbox
```

Explicit LAN source reference:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "把 LAN AP field list ingest 到 wiki，主题是 AP fields" --source "\\LAN\HKC\Discovery\AP_Field_List.txt"
```

## Query Flow

Ask from the wiki after intake:

```bat
py -3 05-ai-factory\scripts\query_wiki.py --query "总结 AP invoice 相关知识，列出 source 和 open questions"
```

The query helper answers only from `03-wiki/` and
`07-references/source-document-index.json`. It reports source pages, source
materials, confidence, open questions, and conflicts.

## Expected Outputs

- Wiki notes under `03-wiki/`
- Open questions under `03-wiki/questions/open-questions.md`
- Conflicts under `03-wiki/questions/conflict-log.md`
- Source index at `07-references/source-document-index.json`
- Intake summary at `06-reports/latest-intake-summary.md`
- Optional SME candidate log under `05-ai-factory/logs/`

`process_intake.py` currently writes the candidate log on each intake run as a
selective-review aid. The candidate log is not itself an SME Review Pack and
does not require SME review unless the item is low-confidence, conflicted,
critical, or otherwise important enough to escalate.

## Optional Selective SME Review

The directories below are retained for selective review, not the default path:

- `05-ai-factory/review-packs/`
- `05-ai-factory/reviewed/`
- `05-ai-factory/prompts/sme-review-chat.md`
- `05-ai-factory/scripts/generate_review_pack.py`
- `05-ai-factory/scripts/apply_reviewed_pack.py`
- `05-ai-factory/scripts/review_candidates.py`

Use optional SME review only for low-confidence items, conflicts, critical
programs, key business fields, and important open questions.

Windows optional review commands:

```bat
py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-WIKI-INTAKE-SAMPLE-001
py -3 05-ai-factory\scripts\review_candidates.py --intake HKC-WIKI-INTAKE-SAMPLE-001
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md
```

Only explicit SME action may produce `SME Confirmed`. Auto Wiki Intake defaults
to `AI Organized`.

## Validation

Run validation after intake:

```bat
py -3 05-ai-factory\scripts\validate_repo.py
```

The validator checks JSON syntax, wiki folders, required reports, source index
shape, review statuses, and that AI wiki notes are not defaulted to
`SME Confirmed`.

## Next-Phase Gaps

These remain intentionally out of scope:

- real LAN folder integration
- real LLM extraction
- RPG / BRD parsing
- target mapping / SDD generation
- Web UI, Excel, pandas, openpyxl, or databases
