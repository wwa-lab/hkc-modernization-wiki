"""Validate repository artifacts for Auto Wiki Intake and optional SME review."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VALID_REVIEW_STATUSES = {
    "Draft",
    "Pending Review",
    "AI Organized",
    "Human Touched",
    "SME Corrected",
    "SME Reviewed",
    "SME Confirmed",
    "Need Clarification",
    "Need Discussion",
    "Conflict",
    "Deprecated",
    "Rejected / Not Applicable",
}
REQUIRED_WIKI_FILES = [
    ROOT / "03-wiki" / "README.md",
    ROOT / "03-wiki" / "index.md",
    ROOT / "03-wiki" / "log.md",
    ROOT / "03-wiki" / "overview" / "README.md",
    ROOT / "03-wiki" / "overview" / "project-background.md",
    ROOT / "03-wiki" / "overview" / "scope-reference.md",
    ROOT / "03-wiki" / "overview" / "system-overview.md",
    ROOT / "03-wiki" / "overview" / "program-notes.md",
    ROOT / "03-wiki" / "legacy" / "README.md",
    ROOT / "03-wiki" / "legacy" / "file-notes.md",
    ROOT / "03-wiki" / "legacy" / "batch-flow-notes.md",
    ROOT / "03-wiki" / "legacy" / "interface-notes.md",
    ROOT / "03-wiki" / "modernization" / "README.md",
    ROOT / "03-wiki" / "modernization" / "engineering-principles.md",
    ROOT / "03-wiki" / "modernization" / "sdd-working-notes.md",
    ROOT / "03-wiki" / "modernization" / "migration-patterns.md",
    ROOT / "03-wiki" / "modernization" / "technical-decisions.md",
    ROOT / "03-wiki" / "data" / "README.md",
    ROOT / "03-wiki" / "data" / "data-dictionary-notes.md",
    ROOT / "03-wiki" / "data" / "field-meaning-notes.md",
    ROOT / "03-wiki" / "data" / "code-value-notes.md",
    ROOT / "03-wiki" / "questions" / "README.md",
    ROOT / "03-wiki" / "questions" / "open-questions.md",
    ROOT / "03-wiki" / "questions" / "conflict-log.md",
]
REQUIRED_FRONTMATTER_FIELDS = [
    "page_type",
    "domain",
    "status",
    "last_updated",
    "source_count",
    "confidence",
    "related_sources",
]
DICTIONARY_REQUIRED_FIELDS = {
    "legacy-programs.json": [
        "program_id",
        "legacy_object",
        "description",
        "source_material_ids",
        "review_source",
        "last_updated",
        "review_status",
    ],
    "legacy-fields.json": [
        "file",
        "field",
        "legacy_object",
        "description",
        "source_material_ids",
        "review_source",
        "last_updated",
        "review_status",
    ],
}
DICTIONARY_KEY_FIELDS = {
    "legacy-programs.json": ["program_id"],
    "legacy-fields.json": ["file", "field"],
}
REVIEW_PACK_REQUIRED_LABELS = [
    "Item ID",
    "Type",
    "Legacy object",
    "AI Recommended Answer",
    "Evidence",
    "Confidence",
    "Alternative Answers",
    "SME Selected Option",
    "SME Selected Alternative",
    "SME Corrected Answer",
    "SME Comment",
    "Review Status",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_json_files(errors: list[str]) -> int:
    count = 0
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts:
            continue
        count += 1
        try:
            load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
    return count


def validate_dictionaries(errors: list[str]) -> int:
    checked = 0
    dictionary_dir = ROOT / "03-dictionaries"
    for filename, required_fields in DICTIONARY_REQUIRED_FIELDS.items():
        path = dictionary_dir / filename
        data = load_json(path)
        if not isinstance(data, list):
            errors.append(f"{path}: top-level JSON must be an array")
            continue
        seen_keys: set[tuple[Any, ...]] = set()
        for index, item in enumerate(data, start=1):
            checked += 1
            if not isinstance(item, dict):
                errors.append(f"{path}[{index}]: dictionary item must be an object")
                continue
            missing = [field for field in required_fields if not item.get(field)]
            if missing:
                errors.append(f"{path}[{index}]: missing required field(s): {', '.join(missing)}")
            status = item.get("review_status")
            if status not in VALID_REVIEW_STATUSES:
                errors.append(f"{path}[{index}]: invalid review_status: {status}")
            if status == "SME Confirmed" and item.get("sme_selected_option") == "Pending Review":
                errors.append(f"{path}[{index}]: Pending Review item was written as SME Confirmed")
            if status == "SME Confirmed" and item.get("sme_selected_option") not in {"A", "B", "C"}:
                errors.append(f"{path}[{index}]: SME Confirmed item must come from option A, B, or C")
            key_fields = DICTIONARY_KEY_FIELDS[filename]
            key = tuple(item.get(field) for field in key_fields)
            if key in seen_keys:
                errors.append(f"{path}[{index}]: duplicate dictionary key {key}")
            seen_keys.add(key)
    return checked


def validate_candidate_logs(errors: list[str]) -> int:
    checked = 0
    logs_dir = ROOT / "05-ai-factory" / "logs"
    if not logs_dir.exists():
        return checked
    for path in logs_dir.glob("*-candidates.json"):
        data = load_json(path)
        candidates = data.get("candidates") if isinstance(data, dict) else None
        if not isinstance(candidates, list):
            errors.append(f"{path}: missing candidates list")
            continue
        for item in candidates:
            checked += 1
            if item.get("review_status") not in VALID_REVIEW_STATUSES:
                errors.append(f"{path}: invalid candidate review_status for {item.get('item_id')}")
            if item.get("review_status") == "SME Confirmed" and "mock extraction" in str(data.get("created_from", "")):
                errors.append(f"{path}: AI-generated candidate defaults to SME Confirmed")
    return checked


def item_sections(markdown: str) -> list[str]:
    pattern = re.compile(r"^##\s+(?:Reviewed|Review) Item\s+\d+\s*$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append(markdown[match.start() : end])
    return sections


def validate_review_packs(errors: list[str]) -> int:
    checked = 0
    for directory in [ROOT / "05-ai-factory" / "review-packs", ROOT / "05-ai-factory" / "reviewed"]:
        for path in directory.glob("*.md"):
            markdown = path.read_text(encoding="utf-8")
            sections = item_sections(markdown)
            for section in sections:
                checked += 1
                for label in REVIEW_PACK_REQUIRED_LABELS:
                    if f"- {label}:" not in section:
                        errors.append(f"{path}: review item missing field: {label}")
                if "A: Accept AI Recommended Answer" not in section:
                    errors.append(f"{path}: review item missing option A")
                if "E: Not Applicable / Not Correct" not in section:
                    errors.append(f"{path}: review item missing option E")
                selected = find_field(section, "SME Selected Option")
                selected_alternative = find_field(section, "SME Selected Alternative")
                status = find_field(section, "Review Status")
                if selected == "Pending Review" and status == "SME Confirmed":
                    errors.append(f"{path}: Pending Review item marked SME Confirmed")
                if status and status not in VALID_REVIEW_STATUSES:
                    errors.append(f"{path}: invalid Review Status: {status}")
                if selected == "B":
                    alternatives = parse_alternatives(section)
                    alternative_index = parse_selected_alternative(selected_alternative)
                    if alternative_index is None:
                        errors.append(f"{path}: option B requires numeric SME Selected Alternative")
                    elif alternative_index < 1 or alternative_index > len(alternatives):
                        errors.append(f"{path}: selected alternative {alternative_index} is out of range")
                if selected in {"A", "B", "C"} and status != "SME Confirmed":
                    errors.append(f"{path}: option {selected} must have Review Status SME Confirmed")
    return checked


def parse_alternatives(section: str) -> list[str]:
    match = re.search(r"^-\s+Alternative Answers:\s*$", section, re.MULTILINE)
    if not match:
        return []
    alternatives = []
    for line in section[match.end() :].splitlines():
        stripped = line.strip()
        if line.startswith("- ") or line.startswith("## "):
            break
        if re.match(r"^\d+\.\s+", stripped):
            alternatives.append(stripped)
    return alternatives


def parse_selected_alternative(value: str) -> int | None:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def validate_reports(errors: list[str]) -> int:
    required_reports = [
        ROOT / "06-reports" / "latest-intake-summary.md",
        ROOT / "06-reports" / "latest-open-question-report.md",
        ROOT / "06-reports" / "latest-review-status-report.md",
    ]
    checked = 0
    for path in required_reports:
        checked += 1
        if not path.exists():
            errors.append(f"{path}: required report is missing")
            continue
        if not path.read_text(encoding="utf-8").strip():
            errors.append(f"{path}: required report is empty")
    return checked


def validate_wiki(errors: list[str]) -> int:
    checked = 0
    for path in REQUIRED_WIKI_FILES:
        checked += 1
        if not path.exists():
            errors.append(f"{path}: required wiki file is missing")
            continue
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            errors.append(f"{path}: required wiki file is empty")
        if not content.startswith("---\n"):
            errors.append(f"{path}: missing frontmatter")
        else:
            frontmatter_end = content.find("\n---\n", 4)
            frontmatter = content[:frontmatter_end] if frontmatter_end != -1 else content
            for field in REQUIRED_FRONTMATTER_FIELDS:
                if f"{field}:" not in frontmatter:
                    errors.append(f"{path}: frontmatter missing field: {field}")
        if "- Status: SME Confirmed" in content and "SME explicit" not in content:
            errors.append(f"{path}: wiki note appears to default to SME Confirmed")
    index_path = ROOT / "03-wiki" / "index.md"
    if index_path.exists():
        index_content = index_path.read_text(encoding="utf-8")
        if "| Page | Purpose | Status | Last Updated | Source Count |" not in index_content:
            errors.append(f"{index_path}: missing wiki index table")
    log_path = ROOT / "03-wiki" / "log.md"
    if log_path.exists():
        log_content = log_path.read_text(encoding="utf-8")
        if "## [" not in log_content or "ingest |" not in log_content:
            errors.append(f"{log_path}: missing parseable operation log entry")
    return checked


def validate_source_index(errors: list[str]) -> int:
    path = ROOT / "07-references" / "source-document-index.json"
    if not path.exists():
        errors.append(f"{path}: source index is missing")
        return 0
    data = load_json(path)
    if not isinstance(data, list):
        errors.append(f"{path}: top-level JSON must be an array")
        return 0
    checked = 0
    required_fields = ["material_id", "source_path", "material_type", "intake_id", "wiki_status", "confidence"]
    for index, item in enumerate(data, start=1):
        checked += 1
        if not isinstance(item, dict):
            errors.append(f"{path}[{index}]: source index item must be an object")
            continue
        missing = [field for field in required_fields if not item.get(field)]
        if missing:
            errors.append(f"{path}[{index}]: missing required field(s): {', '.join(missing)}")
        if item.get("wiki_status") == "SME Confirmed":
            errors.append(f"{path}[{index}]: AI source index entry must not default to SME Confirmed")
        if item.get("wiki_status") not in VALID_REVIEW_STATUSES:
            errors.append(f"{path}[{index}]: invalid wiki_status: {item.get('wiki_status')}")
    return checked


def find_field(section: str, label: str) -> str:
    match = re.search(rf"^-\s+{re.escape(label)}:\s*(.*)$", section, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description="Validate repository JSON and review artifacts.").parse_args()


def main() -> int:
    parse_args()
    errors: list[str] = []
    json_count = validate_json_files(errors)
    dictionary_count = validate_dictionaries(errors)
    candidate_count = validate_candidate_logs(errors)
    review_item_count = validate_review_packs(errors)
    report_count = validate_reports(errors)
    wiki_count = validate_wiki(errors)
    source_index_count = validate_source_index(errors)

    print("Validation Summary")
    print(f"- JSON files checked: {json_count}")
    print(f"- Dictionary items checked: {dictionary_count}")
    print(f"- Candidate items checked: {candidate_count}")
    print(f"- Markdown review items checked: {review_item_count}")
    print(f"- Reports checked: {report_count}")
    print(f"- Wiki files checked: {wiki_count}")
    print(f"- Source index entries checked: {source_index_count}")

    if errors:
        print("- Result: FAILED")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("- Result: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
