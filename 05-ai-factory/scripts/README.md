# Scripts

No complex Python scripts are included in this baseline.

Future scripts may include:

- `process_intake.py` - read intake JSON files and prepare normalized review candidates.
- `generate_review_pack.py` - generate Markdown SME Review Packs from intake candidates.
- `apply_reviewed_pack.py` - apply accepted or corrected reviewed results to JSON dictionaries and mapping candidates.
- `validate_repo.py` - validate repository structure, JSON syntax, review-pack formatting, and required fields.

Python command examples must use Windows-style `py -3` commands.

Example:

```powershell
py -3 05-ai-factory/scripts/validate_repo.py
py -3 05-ai-factory\scripts\validate_repo.py
```

Do not use Excel, pandas, openpyxl, a database, or a web framework for the baseline workflow.

The foundation phase should not implement complex RPG, BRD, or source-document extraction logic. Future scripts should use the Python standard library first and keep JSON and Markdown formats simple.
