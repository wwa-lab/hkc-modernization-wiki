# 真实场景测试指南

状态：Draft

英文版本：
`05-ai-factory/design/real-scenario-test-guideline.md`

这份指南说明如何用 HKC 内部真实材料测试当前 MVP，同时避免把 LAN
文件夹里的原始文档复制进仓库。

## 当前能力边界

当前 MVP 可以处理：

- `05-ai-factory/intake/` 下的 intake JSON
- inbox 目录里的受控 Markdown/text 笔记
- 作为引用登记的 LAN/source 路径

当前 MVP 不会直接读取或解析真实 LAN 文档。通过 `--source` 传入的 LAN
路径只会被记录为 source reference，文件内容不会被 ingest。

真实场景测试时，请使用人工准备的受控笔记来总结真实证据，并引用原始
LAN 路径。不要把完整 BRD、会议纪要、截图、签核文件、导出文件或原始
source code 复制进这个 repo。

## 推荐试点范围

选择一个 reviewer 可以一次看完的窄切片。

适合的试点切片：

- 一个业务流程，例如 AP invoice review 或 order entry
- 一个 legacy program，以及相关 files 和 fields
- 一个有明确输入输出的 batch/job flow
- 一个 interface list，包含少量不确定项

第一轮试点尽量小：

- 1 到 3 份受控笔记
- 3 到 8 个真实 source reference
- 5 到 20 条简洁事实或问题
- 至少 1 个低置信度项
- 至少 1 个可以让 SME 确认的项

## 角色

- BA 或 discovery owner：基于真实材料准备受控笔记。
- SME：只验证 legacy meaning。
- Engineering 或 AI operator：运行脚本并检查 git diff。
- Core-system reviewer：只消费已确认知识和 open questions。

## 安全规则

- LAN folder 仍然是 raw source of truth。
- 仓库里存 source path 和短摘要，不存 raw document copy。
- 测试笔记里不要包含 secret、credential、个人数据或客户敏感细节。
- 不要粘贴完整 BRD 段落、会议纪要、截图或 source code。
- SME review 使用 legacy 语言：program、file、field、job、report、
  screen、interface、batch flow。
- 不要让 SME 验证 API、Java service、target architecture、cloud
  deployment 或 domain model。

## 真实测试方式 A：临时 Inbox 试跑

适用于第一次安全试跑：团队想测试行为，但暂时不想把试点笔记加入 repo。

1. 在 repo 外创建临时目录。

Windows 示例：

```bat
mkdir C:\HKC-wiki-pilot\inbox
```

2. 在该目录加入一份或多份受控笔记。

笔记格式示例：

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

3. 对临时 inbox 运行 Auto Wiki Intake。

Windows：

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 HKC wiki inbox，主题是 AP invoice field pilot" --inbox C:\HKC-wiki-pilot\inbox
py -3 05-ai-factory\scripts\validate_repo.py
```

macOS：

```bash
python3 05-ai-factory/scripts/process_intake.py --request "Process HKC wiki inbox for AP invoice field pilot" --inbox /tmp/HKC-wiki-pilot/inbox
python3 05-ai-factory/scripts/validate_repo.py
```

### 自然语言入口

内部同事也可以用自然语言描述要处理的资料和主题，不需要手写 intake
JSON。当前脚本会把自然语言 request 转成
`05-ai-factory/intake/latest-auto-intake.json`，然后执行 Auto Wiki Intake。

适合这样说：

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理这批 AP invoice controlled notes，主题是 AP invoice field pilot，请只登记 LAN source path，不复制原始文档" --inbox C:\HKC-wiki-pilot\inbox
```

如果已经有一个明确 LAN source path，也可以直接放进自然语言 request：

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "把 `\\LAN\HKC\Discovery\AP\AP_Field_List.xlsx` 登记为 AP invoice field pilot 的 source reference，并处理 inbox 里的 controlled notes" --inbox C:\HKC-wiki-pilot\inbox
```

也可以用 `--source` 明确传入 source path：

```bat
py -3 05-ai-factory\scripts\process_intake.py --request "处理 AP invoice field pilot，使用 inbox controlled notes，并登记 AP field list 作为 source reference" --inbox C:\HKC-wiki-pilot\inbox --source "\\LAN\HKC\Discovery\AP\AP_Field_List.xlsx"
```

自然语言 request 的验收重点：

- `latest-auto-intake.json` 中的 `description` 能表达本次主题
- `materials` 中包含临时 inbox 的 controlled notes
- 明确给出的 LAN path 只作为 `source_path` 被登记
- 没有把 LAN 文件内容复制进 repo
- 生成结果仍需通过 `validate_repo.py`

4. Review 生成结果。

检查：

- `06-reports/latest-intake-summary.md`
- `07-references/source-document-index.json`
- `03-wiki/` 下更新过的页面
- `03-wiki/questions/open-questions.md`
- `03-wiki/questions/conflict-log.md`
- `05-ai-factory/logs/*-candidates.json`

5. 保留任何输出前，先检查 git diff。

```bash
git diff --stat
git diff
```

通过标准：

- source path 只作为 reference 出现
- wiki 输出简洁、可追踪
- 不确定项进入 open questions 或 optional candidates
- 没有 raw document content 被复制进 repo
- `validate_repo.py` 通过

## 真实测试方式 B：正式 Intake Manifest

适用于团队需要可重复的内部测试记录。

1. 准备一份受控笔记。只有当内容已被批准可以进入仓库时，才把它放在
   `05-ai-factory/inbox/` 作为 committed pilot fixture。否则请放在
   repo 外。

2. 创建 intake JSON，同时登记受控笔记和原始 LAN 引用。

示例：

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

3. 运行 manifest。

Windows：

```bat
py -3 05-ai-factory\scripts\process_intake.py --intake 05-ai-factory\intake\HKC-REAL-PILOT-AP-001.json
py -3 05-ai-factory\scripts\validate_repo.py
```

4. 只有在需要时才生成 review material。

```bat
py -3 05-ai-factory\scripts\generate_review_pack.py --intake HKC-REAL-PILOT-AP-001
```

5. 只让 SME review 不确定或重要的项。使用 A/B/C/D/E：

- A：接受 AI Recommended Answer
- B：选择 Alternative Answer
- C：提供 Corrected Answer
- D：Need Discussion
- E：Not Applicable / Not Correct

6. apply reviewed results 前先 dry-run。

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\<reviewed-pack>.md --dry-run
```

7. reviewed pack 看起来正确后，再带 backup apply。

```bat
py -3 05-ai-factory\scripts\apply_reviewed_pack.py --reviewed-pack 05-ai-factory\reviewed\<reviewed-pack>.md --backup
py -3 05-ai-factory\scripts\validate_repo.py
```

通过标准：

- A/B/C 项成为 SME-confirmed program 或 field dictionary entry。
- D 项出现在 open questions。
- E 项出现在 review status report，且不进入 dictionaries。
- 除非未来加入 apply support，否则 files/jobs dictionaries 保持不变。
- Mapping JSON files 保持不变；mapping generation 属于未来工作。

## 真实场景验收 Checklist

接受试点前，请确认：

- `validate_repo.py` 通过。
- `python3 -m unittest discover -s 05-ai-factory/tests` 或
  `py -3 -m unittest discover -s 05-ai-factory\tests` 通过。
- 没有 raw LAN document 被复制进 repo。
- 每条真实 claim 都能追溯到 source path、controlled note 或 reviewed SME
  answer。
- AI-organized content 没有被标为 `SME Confirmed`。
- SME-confirmed dictionary entries 只来自 A/B/C reviewed items。
- Open questions 和 conflicts 在 reports 中可见。
- git diff 只包含预期的 wiki、report、source index、candidate、review 或
  dictionary 变更。

## 内部汇报内容

每个真实场景试点记录：

- pilot topic 和 intake ID
- source material 数量
- controlled note 数量
- 更新的 wiki pages
- open question 数量
- conflict 数量
- optional SME candidate 数量
- SME-confirmed dictionary update 数量
- unresolved decisions
- validation 和 tests 是否通过

## Stop Conditions

如果出现以下情况，停止试点，不要 apply reviewed results：

- note 里包含整段复制的 raw BRD、meeting 或 source-code content
- generated output 中出现 sensitive data 或 credentials
- AI-organized item 被标为 `SME Confirmed`
- reviewed pack 中 A/B/C 没有明确 SME action
- B selection 没有 numeric alternative
- C selection 没有 corrected answer
- validation 失败
- 输出要求 SME review target architecture 或 implementation design
