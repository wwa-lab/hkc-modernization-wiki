# Scripts

This directory contains the MVP script flow for the foundation baseline.

- `process_intake.py` - read intake JSON files and prepare normalized review candidates.
- `generate_review_pack.py` - generate Markdown SME Review Packs from intake candidates.
- `review_candidates.py` - review candidate items with keyboard selection and write reviewed Markdown.
- `apply_reviewed_pack.py` - apply accepted or corrected reviewed results to JSON dictionaries and mapping candidates.
- `validate_repo.py` - validate repository structure, JSON syntax, review-pack formatting, and required fields.

The MVP uses only the Python standard library. It does not use Excel, pandas,
openpyxl, a database, a web framework, real LAN folder reads, or a real LLM API.

## Windows MVP Flow

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-intake.json

py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-INTAKE-SAMPLE-001

py -3 05-ai-factory\scripts\review_candidates.py --intake HKC-INTAKE-SAMPLE-001

py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md

py -3 05-ai-factory\scripts\validate_repo.py
```

For an interactive review output, apply the generated file instead:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\HKC-INTAKE-SAMPLE-001-interactive-reviewed-pack.md
```

## Outputs

- Candidates JSON: `05-ai-factory\logs\<intake_id>-candidates.json`
- SME Review Pack: `05-ai-factory\review-packs\<intake_id>-sme-review-pack.md`
- Interactive reviewed pack: `05-ai-factory\reviewed\<intake_id>-interactive-reviewed-pack.md`
- Program dictionary updates: `03-dictionaries\legacy-programs.json`
- Field dictionary updates: `03-dictionaries\legacy-fields.json`
- Open questions: `06-reports\latest-open-question-report.md`
- Review log: `06-reports\latest-review-status-report.md`

The foundation phase still does not implement complex RPG, BRD, or source-document extraction logic. Future scripts should keep JSON and Markdown formats simple until the real integration phase begins.
