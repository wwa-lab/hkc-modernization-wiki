# HKC Modernization Engineering

This repository contains the engineering foundation for the HKC modernization effort.

It is used for:

- Engineering standards and review rules
- Legacy dictionaries for programs, files, fields, jobs, reports, screens, and batch flows
- AI review workflow definitions
- SME Review Packs
- Mapping candidates between legacy objects and target implementation objects
- Technical knowledge produced during modernization analysis
- Source references and lightweight traceability back to LAN-folder materials

## What This Repository Is Not

This repository is not a replacement for the LAN folder.

The LAN folder remains the source of truth for raw project documents, BRDs, meeting notes, sign-off files, exported legacy materials, screenshots, and original business or technical evidence.

This repository should reference LAN-folder documents where needed, but it should not become an uncontrolled copy of the raw document store. Do not copy full BRDs, raw requirement documents, meeting minutes, sign-off packages, or other original project materials into this repo.

## Review Workflow

SME review is designed for GitHub Copilot Chat first.

AI-generated review packs should be written in Markdown so that Copilot Chat can guide the SME through one item at a time.

The SME does not need to understand Git, JSON, YAML, Markdown editing, APIs, Java services, domain models, service decomposition, or target architecture.

The SME should normally answer choice-based questions, such as `A`, `B`, `C`, `D`, or `E`. The SME may also provide a short natural language correction when the listed choices are not sufficient.

SME questions must focus only on legacy facts, such as program purpose, file meaning, field meaning, code values, job timing, batch flow, screens, reports, and program-file relationships.

## File Formats

- SME Review Packs use Markdown.
- Machine-readable dictionaries use JSON.
- Machine-readable mapping candidates use JSON.
- Windows command examples use `py -3`.

## Environment Constraints

This baseline does not use Excel, pandas, openpyxl, a database, or a web framework.

Future automation should use simple Python scripts that can run in a Windows environment with commands such as:

```powershell
py -3 05-ai-factory/scripts/validate_repo.py
py -3 05-ai-factory\scripts\validate_repo.py
```

This baseline does not implement extraction logic. Future scripts may process intake JSON, generate Markdown review packs, apply reviewed Markdown, and validate repository structure.

Foundation changes are tracked in `CHANGELOG.md`.

## MVP Demo Runbook

The current sample AI factory flow is documented in
`05-ai-factory/README.md`. It includes macOS and Windows commands, terminal
interactive review, Copilot Chat review, expected outputs, validation, and
troubleshooting.
