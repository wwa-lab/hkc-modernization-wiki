# Natural Language Intake Prompt

Use this prompt when the user asks in ordinary language to update the HKC wiki.

## Goal

Turn a user request into intake metadata, then run Auto Wiki Intake.

The user should be able to say:

- `处理 HKC wiki inbox，主题是 invoice matching。`
- `把 \\LAN\\HKC\\Discovery\\AP_Field_List.txt 作为 source reference ingest 到 wiki。`
- `把今天 vendor 给的 AP interface notes 整理进 HKC wiki。`

## Rules

- Do not require the user to hand-write JSON.
- Generate `05-ai-factory/intake/latest-auto-intake.json`.
- Set `project` to `HKC Modernization`.
- Set `submitted_by` to `Agent from user request`.
- Set `submitted_date` to today's date.
- Preserve the original user request in the generated JSON.
- If the request mentions inbox, scan `05-ai-factory/inbox/`.
- If the request includes a LAN path, record it as a source reference and do not copy raw content.
- If the request only gives a topic, scan inbox automatically.
- If inbox is empty and no source path is available, ask one short question for the source path or folder.
- Keep all generated wiki content at `AI Organized` unless explicit SME confirmation exists.

## Command

Windows:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 HKC wiki inbox，主题是 AP invoice field review"
py -3 05-ai-factory\scripts\validate_repo.py
```

For explicit source references:

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "把 LAN AP field list ingest 到 wiki，主题是 AP fields" --source "\\LAN\HKC\Discovery\AP_Field_List.txt"
py -3 05-ai-factory\scripts\validate_repo.py
```

## Report Back

After processing, summarize:

- Generated intake ID
- Sources used
- Pages updated
- Open questions
- Conflicts
- Validation result
