# Repository Usage Guide

This repository is the structured engineering workspace for HKC modernization analysis.

Use it to maintain standards, dictionaries, mapping candidates, review packs, reviewed results, reports, references, and decisions.

Do not use it as the raw document repository. The LAN folder remains the source of truth for raw source documents and project evidence.

## Expected Use

- Store machine-readable dictionaries as JSON.
- Store SME Review Packs as Markdown.
- Store reviewed SME outputs as Markdown.
- Store mapping candidates as JSON.
- Reference LAN-folder source documents through indexes.

## Windows Commands

Python command examples must use `py -3`.

Example:

```powershell
py -3 05-ai-factory/scripts/validate_repo.py
py -3 05-ai-factory\scripts\validate_repo.py
```

The LAN folder remains the source of truth for raw project documents. Do not copy full BRDs, meeting notes, sign-off files, or raw requirement documents into this repository.
