---
page_type: readme
domain: wiki
status: AI Organized
last_updated: 2026-06-19
source_count: 0
confidence: Medium
related_sources: []
---

# HKC Modernization Wiki

This directory is the working LLM wiki for HKC modernization engineering.

The wiki stores AI-organized notes, human corrections, SME confirmations, open
questions, conflicts, and engineering decisions in Markdown. It does not replace
the LAN folder. The LAN folder remains the raw source of truth for original
documents and evidence.

## Three-Layer Architecture

This repo adapts the LLM Wiki pattern to HKC modernization without adopting a
desktop app, MCP server, HTTP API, database, UI, or Obsidian-specific config.

### Raw Sources

Raw sources are LAN-folder documents, vendor materials, and controlled inbox
references.

- They are immutable from the wiki workflow's point of view.
- The LLM reads or references them but does not rewrite them.
- The LAN folder remains the source of truth for raw documents.

### Wiki

The wiki is the LLM-generated Markdown layer under `03-wiki/`.

- `index.md` is the navigation entry for LLM agents and human readers.
- `log.md` is the append-only operation log for ingest, query, and lint actions.
- Wiki notes should preserve source references, confidence, and review status.
- Cross-references should use `[[wikilink]]` where useful.

### Schema

The schema layer constrains the agent.

- `.github/copilot-instructions.md`
- `05-ai-factory/prompts/`
- `01-standards/`

These files define allowed workflows, review status rules, source handling, and
what the agent must not do.

## Areas

- `overview/` - project context, scope, system overview, and program notes.
- `legacy/` - legacy system notes, file notes, batch flows, and interfaces.
- `modernization/` - modernization principles, SDD working notes, patterns, and decisions.
- `data/` - data dictionary notes, field meanings, and code values.
- `questions/` - open questions and conflict log.

## Status Rules

Default AI output is `AI Organized`.

Only explicit SME confirmation can move content to `SME Confirmed`.

## Core Operations

- Ingest: integrate new LAN references or inbox samples into wiki pages, source
  index, open questions, conflict log, `index.md`, and `log.md`.
- Query: answer from wiki pages and source index only, with source page and
  source material references.
- Lint: health-check links, stale notes, conflicts, duplicate notes, missing
  sources, and unresolved questions.
