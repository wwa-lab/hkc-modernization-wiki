# AI Factory Demo Runbook

This runbook demonstrates the MVP script flow from sample intake to validated
dictionary/report updates.

The demo is intentionally local and lightweight:

- Python standard library only
- Markdown for SME review packs
- JSON for machine-readable data
- No Excel, pandas, openpyxl, database, Web UI, real LLM API, or real LAN folder read
- No complex RPG or BRD parsing

## Demo Flow

```text
sample-intake.json
-> process_intake.py
-> candidates JSON
-> generate_review_pack.py
-> Markdown SME Review Pack
-> reviewed Markdown
-> apply_reviewed_pack.py
-> dictionaries / reports
-> validate_repo.py
```

## macOS Commands

Run from the repository root.

```bash
python3 05-ai-factory/scripts/process_intake.py --intake 05-ai-factory/intake/sample-intake.json

python3 05-ai-factory/scripts/generate_review_pack.py --intake HKC-INTAKE-SAMPLE-001

python3 05-ai-factory/scripts/review_candidates.py --intake HKC-INTAKE-SAMPLE-001

python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/HKC-INTAKE-SAMPLE-001-interactive-reviewed-pack.md

python3 05-ai-factory/scripts/validate_repo.py
```

To use the prebuilt reviewed sample instead of the interactive reviewer:

```bash
python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/sample-reviewed-pack.md
```

## Windows Commands

Run from the repository root.

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-intake.json

py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-INTAKE-SAMPLE-001

py -3 05-ai-factory\scripts\review_candidates.py --intake HKC-INTAKE-SAMPLE-001

py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\HKC-INTAKE-SAMPLE-001-interactive-reviewed-pack.md

py -3 05-ai-factory\scripts\validate_repo.py
```

## Safe Apply Options

Preview a reviewed pack without writing dictionaries or reports:

```bash
python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/sample-reviewed-pack.md --dry-run
```

Windows:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md --dry-run
```

Create a timestamped backup before writing outputs:

```bash
python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/sample-reviewed-pack.md --backup
```

Backups are written under:

```text
05-ai-factory/backups/<timestamp>/
```

To use the prebuilt reviewed sample instead of the interactive reviewer:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md
```

## Review Options

The reviewed Markdown supports five SME choices:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Only A, B, and C write dictionary entries. D writes to the open question report.
E writes to the review log and is excluded from dictionaries.

## Terminal Interactive Review

Use this when an SME wants a choice-based terminal experience.

```bash
python3 05-ai-factory/scripts/review_candidates.py --intake HKC-INTAKE-SAMPLE-001
```

Keyboard behavior:

- Up/Down moves the selected option
- Enter confirms the selected option
- A/B/C/D/E are shortcuts
- B opens an alternative-answer picker
- C prompts for a corrected answer
- Each item prompts for an SME comment

Output:

```text
05-ai-factory/reviewed/HKC-INTAKE-SAMPLE-001-interactive-reviewed-pack.md
```

## Copilot Chat Review

Use this when reviewing inside VS Code with GitHub Copilot Chat.

1. Open `05-ai-factory/review-packs/HKC-INTAKE-SAMPLE-001-sme-review-pack.md`.
2. Ask Copilot Chat to guide the SME one item at a time.
3. Answer with A/B/C/D/E.
4. Save the final reviewed Markdown under `05-ai-factory/reviewed/`.
5. Apply the reviewed pack with `apply_reviewed_pack.py`.

Suggested Copilot Chat prompt:

```text
Please guide me through the currently open SME Review Pack one item at a time.

For each item, show the legacy object, AI recommended answer, evidence,
confidence, alternatives, and A/B/C/D/E options.

Wait for my answer before moving to the next item.
If I choose B, ask which alternative number I select.
If I choose C, ask me for the corrected answer.
Do not ask about JSON, Git, APIs, Java services, target architecture, or domain models.

At the end, output a complete reviewed Markdown pack with SME Selected Option,
SME Selected Alternative, SME Corrected Answer, SME Comment, and Review Status.
```

## Expected Outputs

- Candidates JSON:
  `05-ai-factory/logs/HKC-INTAKE-SAMPLE-001-candidates.json`
- Generated SME Review Pack:
  `05-ai-factory/review-packs/HKC-INTAKE-SAMPLE-001-sme-review-pack.md`
- Interactive reviewed pack:
  `05-ai-factory/reviewed/HKC-INTAKE-SAMPLE-001-interactive-reviewed-pack.md`
- Program dictionary:
  `03-dictionaries/legacy-programs.json`
- Field dictionary:
  `03-dictionaries/legacy-fields.json`
- Open question report:
  `06-reports/latest-open-question-report.md`
- Review status report:
  `06-reports/latest-review-status-report.md`

## Validation

Run validation after applying a reviewed pack.

```bash
python3 05-ai-factory/scripts/validate_repo.py
```

Expected result:

```text
Validation Summary
- Result: PASSED
```

The validator checks JSON syntax, dictionary required fields, review statuses,
review pack required fields, B alternative selections, duplicate dictionary keys,
and required report files.

## Automated Tests

The MVP regression tests use Python standard library `unittest`.

macOS:

```bash
python3 -m unittest discover -s 05-ai-factory/tests
```

Windows:

```bat
py -3 -m unittest discover -s 05-ai-factory\tests
```

## Troubleshooting

If `generate_review_pack.py` cannot find candidates, run `process_intake.py`
first.

If `apply_reviewed_pack.py` fails on option B, check that the reviewed Markdown
contains a numeric `SME Selected Alternative`, such as `2`.

If option C fails, check that `SME Corrected Answer` is not blank or `TBD`.

If the terminal review display looks wrong, widen the terminal window and rerun
`review_candidates.py`. The script wraps text based on terminal width.

If validation fails, read the listed file and line context in the validation
message, fix the reviewed Markdown or JSON output, then rerun validation.

## Next-Phase Gaps

These are intentionally out of scope for the MVP demo:

- real LAN folder integration
- real LLM extraction
- real RPG scan parsing
- Copilot Chat actual SME facilitation hardening
- target mapping / SDD generation
