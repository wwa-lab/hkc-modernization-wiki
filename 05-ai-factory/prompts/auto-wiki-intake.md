# Auto Wiki Intake Prompt

Use this prompt when guiding an agent through the default MVP workflow.

## Mission

Process intake materials into `hkc-modernization-wiki`, a lightweight
Agent-readable knowledge base for HKC modernization discovery.

Default flow:

```text
Materials/LAN references/inbox files
-> Agent intake
-> Auto classification
-> Wiki update
-> Source index update
-> Open questions/conflict log
-> Intake summary
-> Optional SME review only when needed
```

## Constraints

- Use Windows commands with `py -3`.
- Use Python standard library only.
- Do not use pandas, openpyxl, Excel, databases, or Web UI.
- Do not call a real LLM API.
- Do not perform complex RPG, BRD, or source-code parsing.
- Use Markdown for wiki pages and reports.
- Use JSON for metadata, dictionaries, and indexes.
- Treat the LAN folder as the raw document source of truth.
- Never mark AI-generated content as `SME Confirmed`.

## Steps

1. If the user gave a natural language request, generate intake metadata first and save it to `05-ai-factory/intake/latest-auto-intake.json`.
2. Scan the inbox or read intake JSON.
3. Validate required intake fields and material metadata.
4. Classify materials into `overview`, `legacy`, `modernization`, `data`, or `questions`.
5. Extract concise wiki notes only; preserve evidence and source path references.
6. Use `[[wikilink]]` for important legacy programs, files, fields, jobs, and interfaces where useful, for example `[[HKC001R]]`, `[[APPPF]]`, or `[[APPPF.APPSTS]]`.
7. Record source, confidence, and `review_status` for each note.
8. Add or preserve wiki page frontmatter:
   - `page_type`
   - `domain`
   - `status`
   - `last_updated`
   - `source_count`
   - `confidence`
   - `related_sources`
9. Default AI output status to `AI Organized`.
10. If evidence is uncertain, append the item to `03-wiki/questions/open-questions.md`.
11. If evidence conflicts, append the item to `03-wiki/questions/conflict-log.md`.
12. Update `07-references/source-document-index.json`.
13. Update `03-wiki/index.md`.
14. Append an ingest entry to `03-wiki/log.md`.
15. Generate `06-reports/latest-intake-summary.md`.

## Natural Language Intake Rules

- Users do not need to hand-write intake JSON.
- Convert natural language requests into intake metadata before processing.
- Save generated metadata to `05-ai-factory/intake/latest-auto-intake.json`.
- Set `submitted_by` to `Agent from user request`.
- If the request mentions inbox, scan `05-ai-factory/inbox/`.
- If the request gives a LAN path, record the path as a source reference; do not copy the raw document.
- If the request gives only a topic, scan inbox automatically.
- If inbox is empty and no source path exists, ask where the source material is.
- Keep default AI output as `AI Organized`.

## Wiki Operation Files

- `03-wiki/index.md` is the LLM and human navigation entry. Every intake must
  update it with all wiki pages, purpose, status, last updated date, and source
  count.
- `03-wiki/log.md` is append-only. Every intake must add one entry using:

```markdown
## [YYYY-MM-DD] ingest | intake-id-or-name
- Sources:
- Pages updated:
- Open questions:
- Conflicts:
```

## Optional Selective SME Review

Use SME review packs only for:

- low-confidence items
- conflicts
- critical programs
- key business fields
- important open questions

Ask one item at a time. Use IBM iSeries, AS400, RPGLE, CLLE, program, file,
field, job, screen, report, and batch-flow language.

Do not ask SMEs about target architecture, APIs, Java services, domain models,
service decomposition, deployment design, or cloud infrastructure.
