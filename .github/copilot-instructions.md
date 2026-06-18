# GitHub Copilot Instructions

This repository supports HKC modernization engineering, legacy analysis, and SME review.

The LAN folder remains the source of truth for BRDs, meeting notes, sign-off files, raw requirements, exported legacy materials, and original project evidence. This repository stores engineering standards, dictionaries, mapping candidates, prompts, review packs, reviewed results, reports, and source references.

## SME Review Context

The SME may have 20-30 years of IBM iSeries, AS400, RPGLE, and CLLE experience.

Use legacy terms the SME already knows:

- program
- file
- field
- job
- report
- screen
- batch flow
- physical file
- logical file

Do not ask the SME to review target architecture, APIs, Java services, domain models, service decomposition, deployment design, or cloud infrastructure.

## Review Style

Ask one item at a time.

For each review item, always show:

- AI Recommended Answer
- Evidence
- Confidence
- A/B/C/D/E options

The SME can answer with `A`, `B`, `C`, `D`, or `E`, or provide a natural language correction.

If the SME provides a correction, preserve the correction text and convert the result into the standard reviewed Markdown format.

Use these standard options:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Processing rules:

- A: use the AI Recommended Answer and mark the item as `SME Confirmed`.
- B: use the SME-selected alternative answer and mark the item as `SME Confirmed`.
- C: use the SME Corrected Answer and mark the item as `SME Confirmed`.
- D: do not write to final dictionaries or mappings; mark the item as `Need Discussion`.
- E: do not write to final dictionaries or mappings; mark the item as `Rejected / Not Applicable`.

## Output Rules

Generate reviewed Markdown in the standard format used by this repository.

Never mark AI-generated content as `SME Confirmed` unless the SME explicitly accepts it, selects an alternative, or provides a correction.

Do not invent evidence. If evidence is incomplete, mark confidence as low and ask the SME to confirm.

Do not turn SME review into target-solution design. Keep questions focused on the legacy object, meaning, usage, source evidence, and modernization relevance.
