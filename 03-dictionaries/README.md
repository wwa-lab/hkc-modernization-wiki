# Dictionaries

This directory contains machine-readable JSON dictionaries for legacy modernization analysis.

The LAN folder remains the source of truth for raw documents. Dictionary entries should reference source evidence where possible.

Current dictionary files:

- `legacy-programs.json`
- `legacy-files.json`
- `legacy-fields.json`
- `legacy-jobs.json`

Current apply support:

- `apply_reviewed_pack.py` writes SME-confirmed `Program Review` items to
  `legacy-programs.json`.
- `apply_reviewed_pack.py` writes SME-confirmed `Field Review` items to
  `legacy-fields.json`.
- `legacy-files.json` and `legacy-jobs.json` are reserved dictionary surfaces
  until file/job review application is implemented.
