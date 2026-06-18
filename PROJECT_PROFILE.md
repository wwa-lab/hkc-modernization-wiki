# HKC Modernization Engineering Repository Profile

## Purpose

This repository is the engineering knowledge foundation for HKC modernization.

It supports standards, dictionaries, mapping candidates, AI prompts, SME Review Packs, reviewed results, reports, source references, and future SDD-driven development support.

## Boundary

The LAN folder remains the source of truth for raw project materials, including BRDs, meeting notes, sign-off files, raw requirements, exported legacy materials, screenshots, and original business or technical evidence.

This repository stores lightweight references to source materials and reviewed engineering knowledge. It must not become another LAN folder.

## SME Review Model

SME review is GitHub Copilot Chat first.

The SME should not manually edit JSON, YAML, or Markdown. Copilot Chat should ask one review item at a time and accept either an `A`, `B`, `C`, `D`, or `E` answer or a short natural language correction.

SME review must focus on legacy facts:

- program purpose
- file meaning
- field meaning
- code values
- job timing
- batch flow
- report usage
- screen usage
- program-file relationships

SME review must not ask for target architecture, API design, Java service design, domain models, or service decomposition.

## MVP Flow

1. Intake JSON references source material in the LAN folder.
2. AI or a future script generates a Markdown SME Review Pack.
3. GitHub Copilot Chat guides SME review one item at a time.
4. Copilot Chat generates reviewed Markdown.
5. Future scripts apply confirmed results to JSON dictionaries and mapping candidates.
6. Reports track open questions, conflicts, and review status.

## Environment

The expected environment is Windows.

Python examples must use `py -3`.

Do not use Excel, pandas, openpyxl, a database, a web framework, or complex package installation for the foundation workflow.
