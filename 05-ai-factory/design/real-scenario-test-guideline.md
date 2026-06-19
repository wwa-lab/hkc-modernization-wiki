# Real Scenario Test Guideline

Status: Draft

Chinese version:
`05-ai-factory/design/real-scenario-test-guideline.zh-CN.md`

This guideline explains how to test the current MVP with real internal HKC
materials without copying raw LAN documents into the repository.

## Current Capability Boundary

The current MVP can process:

- intake JSON under `05-ai-factory/intake/`
- controlled Markdown/text notes in an inbox directory
- LAN/source paths as references

The current MVP does not read or parse real LAN documents directly. A LAN path
passed through `--source` is recorded as a source reference; its file content is
not ingested.

For real scenario testing, use controlled human-prepared notes that summarize
real evidence, and cite the original LAN paths. Do not copy full BRDs, meeting
minutes, screenshots, sign-off files, exports, or raw source code into this
repo.

## Recommended Pilot Scope

Choose a narrow slice that a reviewer can validate in one sitting.

Good pilot slices:

- one business process, such as AP invoice review or order entry
- one legacy program plus related files and fields
- one batch/job flow with known inputs and outputs
- one interface list with a few uncertain items

Keep the first pilot small:

- 1 to 3 controlled notes
- 3 to 8 real source references
- 5 to 20 concise facts or questions
- at least one low-confidence item
- at least one SME-confirmable item

## Roles

- BA or discovery owner prepares controlled notes from real source material.
- SME validates legacy meaning only.
- Engineering or AI operator runs the scripts and reviews diffs.
- Core-system reviewer consumes only confirmed knowledge and open questions.

## Safety Rules

- Keep the LAN folder as the raw source of truth.
- Store source paths and short summaries, not raw document copies.
- Do not include secrets, credentials, personal data, or customer-sensitive
  details in test notes.
- Do not paste full BRD sections, meeting minutes, screenshots, or source code.
- Use legacy language for SME review: programs, files, fields, jobs, reports,
  screens, interfaces, and batch flows.
- Do not ask SMEs to validate APIs, Java services, target architecture, cloud
  deployment, or domain models.

## Real Test Option A: Temporary Inbox Trial

Use this for a safe first run when the team wants to test behavior without
adding pilot notes to the repository.

1. Create a temporary folder outside the repo.

Windows example:

```bat
mkdir C:\HKC-wiki-pilot\inbox
```

2. Add one or more controlled notes to that folder.

Example note shape:

```markdown
# AP Invoice Field Review Pilot Note

- Source Material References:
  - \\LAN\HKC\Discovery\AP\AP_Field_List.xlsx
  - \\LAN\HKC\Discovery\AP\Invoice_Process_Notes.docx
- Prepared By: BA or discovery owner
- Prepared Date: YYYY-MM-DD
- Review Scope: AP invoice fields and status values

## Legacy Facts

- Field APPSTS appears near AP invoice status handling.
- Code value HOLD appears to mean the invoice is blocked from release.
- Program APINVUPD appears to update invoice status after approval.

## Open Questions

- TMPFLAG may be a temporary processing field and needs SME clarification.
- Confirm whether APPSTS is file-specific or shared across AP files.
```

3. Run Auto Wiki Intake against the temporary inbox.

Windows:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 HKC wiki inbox，主题是 AP invoice field pilot" --inbox C:\HKC-wiki-pilot\inbox
py -3 05-ai-factory\scripts\validate_repo.py
```

macOS:

```bash
python3 05-ai-factory/scripts/process_intake.py --request "Process HKC wiki inbox for AP invoice field pilot" --inbox /tmp/HKC-wiki-pilot/inbox
python3 05-ai-factory/scripts/validate_repo.py
```

### Natural Language Entry

Internal users can describe the source set and pilot topic in natural language;
they do not need to hand-write intake JSON for the first pass. The script turns
the request into `05-ai-factory/intake/latest-auto-intake.json`, then runs Auto
Wiki Intake.

Good request shape:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理这批 AP invoice controlled notes，主题是 AP invoice field pilot，请只登记 LAN source path，不复制原始文档" --inbox C:\HKC-wiki-pilot\inbox
```

If there is a clear LAN source path, include it in the request:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "把 `\\LAN\HKC\Discovery\AP\AP_Field_List.xlsx` 登记为 AP invoice field pilot 的 source reference，并处理 inbox 里的 controlled notes" --inbox C:\HKC-wiki-pilot\inbox
```

Or pass the source path explicitly:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 AP invoice field pilot，使用 inbox controlled notes，并登记 AP field list 作为 source reference" --inbox C:\HKC-wiki-pilot\inbox --source "\\LAN\HKC\Discovery\AP\AP_Field_List.xlsx"
```

Acceptance checks for the natural language request:

- `latest-auto-intake.json` has a useful `description`
- `materials` includes the controlled notes from the temporary inbox
- any explicit LAN path is recorded only as `source_path`
- no LAN file content is copied into the repo
- generated artifacts still pass `validate_repo.py`

4. Review the generated outputs.

Check:

- `06-reports/latest-intake-summary.md`
- `07-references/source-document-index.json`
- updated pages under `03-wiki/`
- `03-wiki/questions/open-questions.md`
- `03-wiki/questions/conflict-log.md`
- `05-ai-factory/logs/*-candidates.json`

5. Review the git diff before keeping any output.

```bash
git diff --stat
git diff
```

Pass criteria:

- source paths are references only
- wiki output is concise and traceable
- uncertain items go to open questions or optional candidates
- no raw document content was copied into the repo
- `validate_repo.py` passes

## Real Test Option B: Formal Intake Manifest

Use this when the team wants a repeatable internal test record.

1. Create a controlled note. It can live in `05-ai-factory/inbox/` for a
   committed pilot fixture only if the content is approved for repository
   storage. Otherwise keep it outside the repo.

2. Create an intake JSON with both the controlled note and the original LAN
   references.

Example:

```json
{
  "intake_id": "HKC-REAL-PILOT-AP-001",
  "project": "HKC Modernization",
  "submitted_by": "Internal Pilot Team",
  "submitted_date": "YYYY-MM-DD",
  "description": "Real scenario pilot for AP invoice field review.",
  "materials": [
    {
      "material_id": "REAL-NOTE-AP-001",
      "source_path": "05-ai-factory/inbox/ap-invoice-field-pilot-note.md",
      "material_type": "legacy_file_field_list",
      "owner": "BA",
      "purpose": "Controlled summary of AP invoice field evidence for pilot testing."
    },
    {
      "material_id": "REAL-LAN-AP-001",
      "source_path": "\\\\LAN\\HKC\\Discovery\\AP\\AP_Field_List.xlsx",
      "material_type": "legacy_file_field_list",
      "owner": "Tech",
      "purpose": "Original AP field list reference; raw content remains in LAN."
    }
  ]
}
```

3. Run the manifest.

Windows:

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\HKC-REAL-PILOT-AP-001.json
py -3 05-ai-factory\scripts\validate_repo.py
```

4. Generate review material only if needed.

```bat
py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-REAL-PILOT-AP-001
```

5. Ask the SME to review only the uncertain or important items. Use A/B/C/D/E:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

6. Dry-run before applying reviewed results.

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\<reviewed-pack>.md --dry-run
```

7. Apply with backup only after the reviewed pack looks correct.

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\<reviewed-pack>.md --backup
py -3 05-ai-factory\scripts\validate_repo.py
```

Pass criteria:

- A/B/C items become SME-confirmed program or field dictionary entries.
- D items appear as open questions.
- E items appear in the review status report and do not enter dictionaries.
- Files/jobs dictionaries remain unchanged unless future apply support is added.
- Mapping JSON files remain unchanged; mapping generation is future work.

## Real Scenario Acceptance Checklist

Before the pilot is accepted, confirm:

- `validate_repo.py` passes.
- `python3 -m unittest discover -s 05-ai-factory/tests` or
  `py -3 -m unittest discover -s 05-ai-factory\tests` passes.
- No raw LAN documents were copied into the repo.
- Every real claim points back to a source path, controlled note, or reviewed
  SME answer.
- AI-organized content is not marked `SME Confirmed`.
- SME-confirmed dictionary entries came only from A/B/C reviewed items.
- Open questions and conflicts are visible in the reports.
- The git diff contains only expected wiki, report, source index, candidate,
  review, or dictionary changes.

## What To Report Internally

For each real scenario pilot, record:

- pilot topic and intake ID
- source material count
- controlled note count
- wiki pages updated
- open question count
- conflict count
- optional SME candidate count
- SME-confirmed dictionary update count
- unresolved decisions
- whether validation and tests passed

## Stop Conditions

Stop the pilot and do not apply reviewed results if:

- a note contains raw BRD/meeting/source-code content copied wholesale
- sensitive data or credentials appear in a generated output
- an AI-organized item is marked `SME Confirmed`
- a reviewed pack has A/B/C without explicit SME action
- a B selection has no numeric alternative
- a C selection has no corrected answer
- validation fails
- the output asks SMEs to review target architecture or implementation design
