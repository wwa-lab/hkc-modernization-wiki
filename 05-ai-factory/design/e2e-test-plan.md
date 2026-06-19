# E2E Test Plan: Core-System Input Preparation Flow

Status: Draft

This test plan verifies that the repository can support an end-to-end flow from
sample intake to reviewed wiki, dictionary, and report artifacts without real
LAN folder integration, real LLM APIs, RPG parsing, databases, Excel, or Web UI.

## Test Objectives

Verify that:

- sample intake can produce review candidates
- candidates can produce a Markdown SME Review Pack
- terminal and Markdown review paths can produce reviewed Markdown
- reviewed Markdown can update dictionaries and reports correctly
- A/B/C/D/E decisions route to the correct outputs
- validation catches structural issues
- dry-run and backup behavior make apply safer
- outputs are suitable as inputs to future core-system review

## Test Constraints

- Use Python standard library only.
- Use JSON for machine-readable artifacts.
- Use Markdown for SME-facing artifacts.
- Do not use pandas, openpyxl, Excel, database, Web UI, real LLM API, or real LAN
  folder reads.
- Windows command examples must use `py -3`.

## Test Environments

macOS local development:

```bash
python3 --version
```

Windows target command style:

```bat
py -3 --version
```

## Test Data

For internal pilots using real source references and controlled notes, use
`05-ai-factory/design/real-scenario-test-guideline.md`.

Primary sample intake:

```text
05-ai-factory/intake/sample-intake.json
```

Primary reviewed sample:

```text
05-ai-factory/reviewed/sample-reviewed-pack.md
```

Expected generated candidates:

```text
05-ai-factory/logs/HKC-INTAKE-SAMPLE-001-candidates.json
```

Expected generated review pack:

```text
05-ai-factory/review-packs/HKC-INTAKE-SAMPLE-001-sme-review-pack.md
```

## E2E Scenario 1: Sample Intake to Candidates

Purpose:

Verify that sample intake can be read and converted into mock review candidates.

macOS:

```bash
python3 05-ai-factory/scripts/process_intake.py --intake 05-ai-factory/intake/sample-intake.json
```

Windows:

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\sample-intake.json
```

Expected:

- candidates JSON is written to `05-ai-factory/logs/`
- candidates contain Program Review and Field Review items
- candidates contain low-confidence examples for Need Discussion and Not
  Applicable / Not Correct paths
- every candidate has source material IDs and uses `AI Organized` or
  `Need Clarification` until explicit SME action

Pass criteria:

- command exits with code 0
- output JSON is valid
- candidate count is at least 4

## E2E Scenario 2: Candidates to SME Review Pack

Purpose:

Verify that candidates can generate a section-based Markdown Review Pack.

macOS:

```bash
python3 05-ai-factory/scripts/generate_review_pack.py --intake HKC-INTAKE-SAMPLE-001
```

Windows:

```bat
py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-INTAKE-SAMPLE-001
```

Expected:

- Review Pack is written to `05-ai-factory/review-packs/`
- each item is a section
- no complex Markdown tables are used
- each item includes A/B/C/D/E options
- SME response fields default to Pending Review or TBD

Pass criteria:

- command exits with code 0
- Review Pack contains all required labels
- `SME Selected Alternative` is present

## E2E Scenario 3: Terminal SME Review

Purpose:

Verify that a reviewer can use keyboard selection to produce reviewed Markdown.

macOS:

```bash
python3 05-ai-factory/scripts/review_candidates.py --intake HKC-INTAKE-SAMPLE-001
```

Windows:

```bat
py -3 05-ai-factory\scripts\review_candidates.py --intake HKC-INTAKE-SAMPLE-001
```

Manual steps:

1. Use Up/Down to move between options.
2. Press Enter to select.
3. Select B for at least one item and choose an alternative number.
4. Select D for at least one item.
5. Select E for at least one item.
6. Enter SME comments or press Enter for TBD.

Expected:

- reviewed Markdown is written to `05-ai-factory/reviewed/`
- selected options are recorded
- B records numeric selected alternative
- D records Need Discussion
- E records SME Reviewed and does not become confirmed

Pass criteria:

- reviewed Markdown validates with `validate_repo.py`
- reviewed Markdown can be applied successfully

## E2E Scenario 4: Copilot Chat SME Review

Purpose:

Verify that Copilot Chat can facilitate one-item-at-a-time SME review using the
Markdown Review Pack.

Manual steps:

1. Open `05-ai-factory/review-packs/HKC-INTAKE-SAMPLE-001-sme-review-pack.md`.
2. Ask Copilot Chat to review one item at a time.
3. Answer A/B/C/D/E.
4. If B, provide the alternative number.
5. If C, provide corrected answer.
6. Save the final reviewed Markdown under `05-ai-factory/reviewed/`.

Expected:

- SME does not need to read JSON
- SME is not asked about target APIs, Java services, domain models, or
  architecture
- final reviewed Markdown preserves required fields

Pass criteria:

- `apply_reviewed_pack.py --dry-run` succeeds
- `validate_repo.py` succeeds after apply

## E2E Scenario 5: Apply Reviewed Pack

Purpose:

Verify that reviewed Markdown updates dictionaries and reports according to
A/B/C/D/E rules.

macOS:

```bash
python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/sample-reviewed-pack.md
```

Windows:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md
```

Expected:

- A writes AI recommended answer to dictionary
- B writes selected alternative to dictionary
- C writes SME corrected answer to dictionary
- D writes open question and does not write dictionary
- E writes review log and does not write dictionary

Pass criteria:

- Program Review writes to `03-dictionaries/legacy-programs.json`
- Field Review writes to `03-dictionaries/legacy-fields.json`
- `PRCADJ` remains out of dictionaries when D
- `TMPFLAG` remains out of dictionaries when E

## E2E Scenario 6: Dry Run

Purpose:

Verify that reviewed Markdown can be parsed and summarized without writing
outputs.

macOS:

```bash
python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/sample-reviewed-pack.md --dry-run
```

Windows:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md --dry-run
```

Expected:

- summary is printed
- dictionaries are unchanged
- reports are unchanged

Pass criteria:

- command exits with code 0
- output includes `dry_run: True`

## E2E Scenario 7: Backup Apply

Purpose:

Verify that current outputs can be backed up before writing changes.

macOS:

```bash
python3 05-ai-factory/scripts/apply_reviewed_pack.py --reviewed-pack 05-ai-factory/reviewed/sample-reviewed-pack.md --backup
```

Windows:

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\sample-reviewed-pack.md --backup
```

Expected:

- backup files are created under `05-ai-factory/backups/<timestamp>/`
- apply still writes current outputs

Pass criteria:

- backup directory exists
- output summary lists backup files
- validation passes after apply

## E2E Scenario 8: Repository Validation

Purpose:

Verify that repository artifacts remain structurally valid.

macOS:

```bash
python3 05-ai-factory/scripts/validate_repo.py
```

Windows:

```bat
py -3 05-ai-factory\scripts\validate_repo.py
```

Expected:

```text
Validation Summary
- Result: PASSED
```

Pass criteria:

- JSON files are valid
- dictionary fields are present
- review statuses are legal
- Review Packs contain required fields
- B selections are numeric and in range
- reports exist

## Automated Regression Tests

macOS:

```bash
python3 -m unittest discover -s 05-ai-factory/tests
```

Windows:

```bat
py -3 -m unittest discover -s 05-ai-factory\tests
```

Expected:

```text
Ran 9 tests
OK
```

## Negative Test Cases

These should fail validation or apply:

- candidate JSON missing required fields
- reviewed item with `SME Selected Option: B` but no numeric selected alternative
- reviewed item with `SME Selected Option: C` but no corrected answer
- reviewed item with `SME Selected Option: A` and `Review Status: Pending Review`
- duplicate dictionary key
- invalid JSON file
- missing required reports

## Core-System Input Readiness Checks

Before an output is used for core-system review, verify:

- dictionaries contain only SME-confirmed A/B/C items
- D items are visible in open question report
- E items are visible in review status report
- source material IDs are preserved
- reviewed pack source is preserved
- assumptions and open questions are not mixed into confirmed knowledge

## Exit Criteria

The E2E flow is acceptable when:

- all scripted scenarios pass
- terminal and Copilot Chat review paths have at least one successful manual run
- `unittest` passes
- `validate_repo.py` passes
- no out-of-scope integrations are introduced
- outputs are ready to support a core-system input package draft
