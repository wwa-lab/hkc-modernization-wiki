# Review Process

The default process is Auto Wiki Intake. SME Review Packs are an optional
selective review mechanism.

## Default Auto Wiki Intake

1. Register materials from LAN references, intake JSON, or controlled inbox files.
2. Validate material metadata.
3. Classify materials into wiki areas.
4. Extract concise Markdown notes with source evidence.
5. Update `03-wiki/`.
6. Update `07-references/source-document-index.json`.
7. Log open questions and conflicts.
8. Generate `06-reports/latest-intake-summary.md`.

Default status for AI output is `AI Organized`.

## Optional Selective SME Review

Use SME review only for:

- low-confidence items
- conflicts
- critical programs
- key business fields
- important open questions

## SME Review Rules

- Ask one item at a time.
- Show the AI Recommended Answer, evidence, confidence, and A/B/C/D/E options.
- Accept either a choice or natural language correction.
- Keep SME questions focused on IBM iSeries, AS400, RPGLE, CLLE, programs,
  files, fields, jobs, screens, reports, and batch flows.
- Do not ask about target architecture, APIs, Java services, domain models,
  service decomposition, deployment design, or cloud infrastructure.
- Never mark AI output as `SME Confirmed` without explicit SME action.
