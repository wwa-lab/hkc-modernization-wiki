# Scripts

This directory contains local MVP scripts.

- `process_intake.py` - default Auto Wiki Intake: read intake JSON or scan inbox, classify materials, update wiki notes, source index, questions/conflicts, and intake summary.
- `query_wiki.py` - answer natural language questions from `03-wiki/` and `source-document-index.json` with source pages and source materials.
- `generate_review_pack.py` - optional selective SME Review Pack generation from candidate logs.
- `review_candidates.py` - optional terminal review for selected candidate items.
- `apply_reviewed_pack.py` - optional application of SME-confirmed program and field review results to JSON dictionaries and reports.
- `validate_repo.py` - validate repository structure, JSON syntax, wiki files, source index, reports, review-pack formatting, and status rules.

The MVP uses only the Python standard library. It does not use Excel, pandas,
openpyxl, a database, a web framework, real LAN folder reads, or a real LLM API.

## Windows Main Flow

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 HKC wiki inbox，主题是 AP invoice field review"
py -3 05-ai-factory\scripts\validate_repo.py
```

The natural language request is converted to
`05-ai-factory\intake\latest-auto-intake.json`.

Explicit intake JSON remains supported:

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-wiki-intake.json
py -3 05-ai-factory\scripts\validate_repo.py
```

## Windows Query Flow

```bat
py -3 05-ai-factory\scripts\query_wiki.py --query "总结 AP invoice 相关知识，列出 source 和 open questions"
```

The query helper reads `03-wiki\index.md`, wiki pages, and
`07-references\source-document-index.json` only.

## Optional Selective SME Review

Use only for low-confidence items, conflicts, critical programs, key business
fields, and important open questions.

```bat
py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-WIKI-INTAKE-SAMPLE-001
py -3 05-ai-factory\scripts\review_candidates.py --intake HKC-WIKI-INTAKE-SAMPLE-001
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md
```

Preview without writing outputs:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md --dry-run
```

## Main Outputs

- Wiki notes: `03-wiki\`
- Source index: `07-references\source-document-index.json`
- Intake summary: `06-reports\latest-intake-summary.md`
- Open questions: `03-wiki\questions\open-questions.md`
- Conflicts: `03-wiki\questions\conflict-log.md`
- Optional candidates JSON: `05-ai-factory\logs\<intake_id>-candidates.json`

`process_intake.py` writes the optional candidates JSON automatically. The
follow-on SME Review Pack and terminal review steps remain optional.

## Tests

```bat
py -3 -m unittest discover -s 05-ai-factory\tests
```
