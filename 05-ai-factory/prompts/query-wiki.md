# Query Wiki Prompt

Use this prompt when answering questions from `hkc-modernization-wiki`, the
lightweight Agent-readable knowledge base for HKC modernization discovery.

## Rules

- Read `03-wiki/index.md` before answering.
- Prefer `05-ai-factory/scripts/query_wiki.py` for repeatable local query output.
- Answer only from `03-wiki/` pages and `07-references/source-document-index.json`.
- Do not use raw LAN-folder content directly unless it is represented in the
  source index.
- Do not call external tools, real LLM APIs, MCP servers, HTTP APIs, databases,
  desktop apps, or UI systems.
- Preserve the difference between `AI Organized`, `Need Clarification`,
  `Conflict`, and `SME Confirmed`.
- Never promote AI-organized content to `SME Confirmed`.

## Answer Format

For each answer, include:

- Direct answer
- Source page or pages
- Source material ID or IDs
- Confidence
- Open questions or conflicts, if any

If the query produces a durable synthesis, suggest archiving it as a new wiki
page under the appropriate `03-wiki/` area. Do not create the page unless the
user asks for that follow-up.

## Command

Windows:

```bat
py -3 05-ai-factory\scripts\query_wiki.py --query "总结 AP invoice 相关知识，列出 source 和 open questions"
```
