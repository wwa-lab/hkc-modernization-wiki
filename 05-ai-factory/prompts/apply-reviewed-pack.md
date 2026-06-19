# Apply Reviewed Pack Prompt

Read a reviewed Markdown pack and identify accepted, corrected, rejected, and open items.

Prepare dictionary updates only from reviewed content.

Current script boundary: `apply_reviewed_pack.py` applies `Program Review` and
`Field Review` items into the supported legacy dictionaries and reports. Mapping
updates are a future reviewed workflow, not a current apply target.

Do not apply pending or unresolved items as approved knowledge.

Only apply items marked `SME Confirmed`.

Do not apply items marked `Need Discussion`, `Rejected / Not Applicable`, `Pending Review`, or `AI Candidate` to final dictionaries.

Never treat AI-generated content as confirmed unless the SME explicitly accepted it, selected an alternative, or provided a correction.
