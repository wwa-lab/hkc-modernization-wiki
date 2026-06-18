# hkc-modernization-wiki Repository Profile

## Purpose

This repository is a lightweight Agent-readable wiki for HKC modernization
discovery.

It supports natural-language intake, wiki notes, source references, query
answers, open questions, conflicts, and optional selective SME review.

## Boundary

The LAN folder remains the source of truth for raw project materials, including BRDs, meeting notes, sign-off files, raw requirements, exported legacy materials, screenshots, and original business or technical evidence.

This repository stores lightweight references to source materials and
AI-organized wiki knowledge. It must not become another LAN folder.

## Daily Model

The normal interaction is conversational:

- The user asks the Agent to ingest inbox or LAN references.
- The Agent creates intake metadata when needed.
- The Agent updates `03-wiki/`, source index, open questions, conflict log, and summary.
- The user later asks the Agent to summarize or query the wiki.
- The Agent answers with source pages, source materials, status, and confidence.

SME review is optional selective review only.

The SME should not manually edit JSON, YAML, or Markdown. Copilot Chat should
ask one review item at a time and accept either an `A`, `B`, `C`, `D`, or `E`
answer or a short natural language correction.

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

1. User gives a natural language ingest request or provides intake JSON.
2. Agent/script creates or reads intake metadata.
3. Auto Wiki Intake updates Markdown wiki pages, source index, open questions,
   conflict log, wiki index, wiki log, and intake summary.
4. User asks natural language questions against the wiki.
5. Query flow answers from `03-wiki/` and `07-references/source-document-index.json`.
6. Optional SME review is used only for low-confidence items, conflicts,
   critical programs, key business fields, and important open questions.

## Environment

The expected environment is Windows.

Python examples must use `py -3`.

Do not use Excel, pandas, openpyxl, a database, a web framework, or complex package installation for the foundation workflow.
