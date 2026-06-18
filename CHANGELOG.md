# Changelog

All notable repository foundation changes should be recorded here.

This changelog tracks engineering baseline changes only. It does not track raw project document changes from the LAN folder.

## 2026-06-18

### Added

- Initial HKC modernization engineering repository foundation.
- Governance, standards, templates, dictionaries, mappings, AI factory, reports, references, and decisions directories.
- GitHub Copilot Chat SME review instructions and prompts.
- Markdown SME Review Pack sample and reviewed sample.
- JSON placeholders for dictionaries, mappings, and source document index.
- Project profile describing repository purpose, boundary, SME review model, MVP flow, and Windows environment constraints.

### Changed

- Standardized SME review options:
  - A: Accept AI Recommended Answer
  - B: Choose Alternative Answer
  - C: Provide Corrected Answer
  - D: Need Discussion
  - E: Not Applicable / Not Correct
- Clarified that AI-generated content must not be marked `SME Confirmed` without explicit SME action.
- Aligned sample intake manifest with the expected JSON intake structure.

### Not Included

- No complex extraction logic.
- No Python scripts implemented yet.
- No Excel, pandas, openpyxl, database, or web framework.
- No copied BRD, meeting notes, sign-off files, or raw LAN-folder project documents.
