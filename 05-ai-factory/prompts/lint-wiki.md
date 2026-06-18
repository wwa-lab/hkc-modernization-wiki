# Lint Wiki Prompt

Use this prompt when health-checking `hkc-modernization-wiki`, the lightweight
Agent-readable knowledge base for HKC modernization discovery.

## Scope

Read:

- `03-wiki/index.md`
- relevant `03-wiki/` pages
- `03-wiki/log.md`
- `07-references/source-document-index.json`

Do not use a desktop app, MCP server, HTTP API, database, UI, real LLM API, or
complex RPG/BRD parser.

## Checks

- Orphan pages with no useful inbound or outbound wikilinks.
- Missing source references in wiki notes.
- Stale `AI Organized` pages that have not been touched recently.
- Contradictions between pages or between page notes and source-index metadata.
- Missing wikilinks for important programs, files, fields, jobs, or interfaces.
- Duplicated notes or repeated claims from the same source.
- Unresolved open questions that have no owner, next step, or source reference.

## Output Format

Group findings by severity:

- Critical
- High
- Medium
- Low

For each finding, include:

- Page
- Evidence
- Suggested fix
- Whether optional SME review is needed

Append a `lint` entry to `03-wiki/log.md` only when the user asks you to record
the lint operation.
