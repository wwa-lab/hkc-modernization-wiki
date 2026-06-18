"""Apply a reviewed Markdown SME pack to JSON dictionaries and reports."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROGRAMS_PATH = ROOT / "03-dictionaries" / "legacy-programs.json"
FIELDS_PATH = ROOT / "03-dictionaries" / "legacy-fields.json"
OPEN_QUESTIONS_PATH = ROOT / "06-reports" / "latest-open-question-report.md"
REVIEW_STATUS_PATH = ROOT / "06-reports" / "latest-review-status-report.md"
VALID_OPTIONS = {"A", "B", "C", "D", "E"}
CONFIRMED_OPTIONS = {"A", "B", "C"}
CONFIRMED_STATUS = "SME Confirmed"


def load_json_array(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def strip_ticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def normalize_value(value: str) -> str:
    value = value.strip()
    return "" if value in {"TBD", "Pending Review"} else value


def parse_sections(markdown: str) -> list[dict[str, Any]]:
    heading_pattern = re.compile(r"^##\s+(?:Reviewed|Review) Item\s+\d+\s*$", re.MULTILINE)
    matches = list(heading_pattern.finditer(markdown))
    items: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        section = markdown[start:end]
        items.append(parse_item_section(section))
    return items


def parse_field(section: str, label: str) -> str:
    pattern = re.compile(rf"^-\s+{re.escape(label)}:\s*(.*)$", re.MULTILINE)
    match = pattern.search(section)
    return normalize_value(match.group(1)) if match else ""


def parse_metadata(markdown: str) -> dict[str, str]:
    metadata_match = re.search(
        r"^##\s+Review Pack Metadata\s*$([\s\S]*?)(?=^##\s+)",
        markdown,
        re.MULTILINE,
    )
    metadata_section = metadata_match.group(1) if metadata_match else markdown
    metadata = {
        "pack_id": strip_ticks(parse_field(metadata_section, "Pack ID")),
        "intake_id": strip_ticks(parse_field(metadata_section, "Intake ID")),
        "source_material_ids": parse_source_material_ids(
            parse_field(metadata_section, "Source Document References")
        ),
    }
    missing = [field for field in ["pack_id", "intake_id"] if not metadata[field]]
    if missing:
        raise ValueError(f"Reviewed pack metadata missing field(s): {', '.join(missing)}")
    return metadata


def parse_source_material_ids(value: str) -> list[str]:
    if not value:
        return []
    return [strip_ticks(part.strip()) for part in value.split(",") if part.strip()]


def parse_bulleted_block(section: str, label: str) -> list[str]:
    pattern = re.compile(rf"^-\s+{re.escape(label)}:\s*$", re.MULTILINE)
    match = pattern.search(section)
    if not match:
        return []
    lines = []
    for line in section[match.end() :].splitlines():
        if line.startswith("- ") or line.startswith("## "):
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            lines.append(re.sub(r"^\d+\.\s+", "", stripped).strip())
        elif stripped:
            break
    return lines


def parse_alternatives(section: str) -> list[str]:
    return parse_bulleted_block(section, "Alternative Answers")


def parse_evidence(section: str) -> list[str]:
    return parse_bulleted_block(section, "Evidence")


def parse_item_section(section: str) -> dict[str, Any]:
    return {
        "item_id": strip_ticks(parse_field(section, "Item ID")),
        "type": parse_field(section, "Type"),
        "legacy_object": strip_ticks(parse_field(section, "Legacy object")),
        "ai_recommended_answer": parse_field(section, "AI Recommended Answer"),
        "why_ai_recommends_this": parse_field(section, "Why AI recommends this"),
        "evidence": parse_evidence(section),
        "confidence": parse_field(section, "Confidence"),
        "alternative_answers": parse_alternatives(section),
        "question_for_sme": parse_field(section, "Question for SME"),
        "sme_selected_option": parse_field(section, "SME Selected Option").upper(),
        "sme_selected_alternative": parse_field(section, "SME Selected Alternative"),
        "sme_corrected_answer": parse_field(section, "SME Corrected Answer"),
        "sme_comment": parse_field(section, "SME Comment"),
        "review_status": parse_field(section, "Review Status"),
    }


def selected_alternative_index(item: dict[str, Any]) -> int:
    value = item["sme_selected_alternative"]
    if not value:
        raise ValueError(f"{item['item_id']} selected B but SME Selected Alternative is blank")
    match = re.search(r"\d+", value)
    if not match:
        raise ValueError(f"{item['item_id']} selected B but SME Selected Alternative is not a number")
    return int(match.group(0)) - 1


def answer_for_item(item: dict[str, Any]) -> str:
    option = item["sme_selected_option"]
    if option == "A":
        return item["ai_recommended_answer"]
    if option == "B":
        alternatives = item["alternative_answers"]
        if not alternatives:
            raise ValueError(f"{item['item_id']} selected B but has no alternative answers")
        index = selected_alternative_index(item)
        if index < 0 or index >= len(alternatives):
            raise ValueError(
                f"{item['item_id']} selected alternative {index + 1}, "
                f"but only {len(alternatives)} alternative answer(s) exist"
            )
        return alternatives[index]
    if option == "C":
        corrected = item["sme_corrected_answer"]
        if not corrected:
            raise ValueError(f"{item['item_id']} selected C but has no corrected answer")
        return corrected
    raise ValueError(f"{item['item_id']} option {option} does not produce a dictionary answer")


def dictionary_entry(item: dict[str, Any], metadata: dict[str, str]) -> dict[str, Any]:
    entry = {
        "item_id": item["item_id"],
        "legacy_object": item["legacy_object"],
        "description": answer_for_item(item),
        "ai_recommended_answer": item["ai_recommended_answer"],
        "sme_selected_option": item["sme_selected_option"],
        "sme_selected_alternative": item["sme_selected_alternative"],
        "sme_comment": item["sme_comment"],
        "source_material_ids": metadata["source_material_ids"],
        "source_evidence": item["evidence"],
        "confidence": item["confidence"],
        "review_source": metadata["pack_id"],
        "intake_id": metadata["intake_id"],
        "last_updated": date.today().isoformat(),
        "review_status": CONFIRMED_STATUS,
    }
    if item["type"] == "Program Review":
        return {"program_id": item["legacy_object"], **entry}
    if item["type"] == "Field Review":
        return {"file": "UNKNOWN", "field": item["legacy_object"], **entry}
    raise ValueError(f"Unsupported review item type: {item['type']}")


def upsert_by_key(items: list[dict[str, Any]], entry: dict[str, Any], key_fields: list[str]) -> bool:
    key = tuple(entry.get(field) for field in key_fields)
    for index, existing in enumerate(items):
        if tuple(existing.get(field) for field in key_fields) == key:
            items[index] = {**existing, **entry}
            return False
    items.append(entry)
    return True


def render_open_questions(items: list[dict[str, Any]]) -> str:
    lines = [
        "# Latest Open Question Report",
        "",
        f"Generated Date: {date.today().isoformat()}",
        "",
    ]
    if not items:
        lines.extend([
            "Status: No open questions have been reported yet.",
            "",
        ])
        return "\n".join(lines)
    for item in items:
        lines.extend(
            [
                f"## {item['item_id']} - {item['legacy_object']}",
                "",
                f"- Type: {item['type']}",
                f"- Question for SME: {item['question_for_sme']}",
                f"- AI Recommended Answer: {item['ai_recommended_answer']}",
                f"- SME Comment: {item['sme_comment'] or 'TBD'}",
                "- Review Status: Need Discussion",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_review_log(applied: list[str], skipped: list[dict[str, Any]]) -> str:
    lines = [
        "# Latest Review Status Report",
        "",
        f"Generated Date: {date.today().isoformat()}",
        "",
        "## Summary",
        "",
        f"- Applied items: {len(applied)}",
        f"- Not applicable / not correct items: {len(skipped)}",
        "",
        "## Applied Items",
        "",
    ]
    if applied:
        lines.extend(f"- {item_id}" for item_id in applied)
    else:
        lines.append("- None")
    lines.extend(["", "## Not Applicable / Not Correct Items", ""])
    if skipped:
        for item in skipped:
            lines.extend(
                [
                    f"- {item['item_id']} `{item['legacy_object']}`",
                    f"  - Type: {item['type']}",
                    f"  - SME Comment: {item['sme_comment'] or 'TBD'}",
                ]
            )
    else:
        lines.append("- None")
    return "\n".join(lines).rstrip() + "\n"


def validate_reviewed_item(item: dict[str, Any]) -> None:
    missing = [field for field in ["item_id", "type", "legacy_object"] if not item.get(field)]
    if missing:
        raise ValueError(f"Reviewed item missing field(s): {', '.join(missing)}")
    if item["sme_selected_option"] not in VALID_OPTIONS:
        raise ValueError(f"{item['item_id']} has invalid SME Selected Option: {item['sme_selected_option']}")
    if item["sme_selected_option"] in CONFIRMED_OPTIONS and item["review_status"] != CONFIRMED_STATUS:
        raise ValueError(
            f"{item['item_id']} selected {item['sme_selected_option']} but Review Status is "
            f"{item['review_status'] or 'blank'}, expected {CONFIRMED_STATUS}"
        )
    if item["sme_selected_option"] == "B":
        selected_alternative_index(item)


def apply_reviewed_pack(path: Path) -> dict[str, int]:
    markdown = path.read_text(encoding="utf-8")
    metadata = parse_metadata(markdown)
    items = parse_sections(markdown)
    if not items:
        raise ValueError("No reviewed item sections found")
    programs = load_json_array(PROGRAMS_PATH)
    fields = load_json_array(FIELDS_PATH)
    open_questions: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    applied: list[str] = []
    inserted_or_updated = 0

    for item in items:
        validate_reviewed_item(item)
        option = item["sme_selected_option"]
        if option in {"A", "B", "C"}:
            entry = dictionary_entry(item, metadata)
            if item["type"] == "Program Review":
                upsert_by_key(programs, entry, ["program_id"])
            elif item["type"] == "Field Review":
                upsert_by_key(fields, entry, ["file", "field"])
            else:
                raise ValueError(f"Unsupported review item type: {item['type']}")
            applied.append(item["item_id"])
            inserted_or_updated += 1
        elif option == "D":
            open_questions.append(item)
        elif option == "E":
            skipped.append(item)

    write_json(PROGRAMS_PATH, programs)
    write_json(FIELDS_PATH, fields)
    OPEN_QUESTIONS_PATH.write_text(render_open_questions(open_questions), encoding="utf-8", newline="\n")
    REVIEW_STATUS_PATH.write_text(render_review_log(applied, skipped), encoding="utf-8", newline="\n")
    return {
        "reviewed_items": len(items),
        "dictionary_updates": inserted_or_updated,
        "open_questions": len(open_questions),
        "not_applicable": len(skipped),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply reviewed Markdown SME pack.")
    parser.add_argument("--reviewed-pack", required=True, help="Path to reviewed Markdown pack.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = apply_reviewed_pack(Path(args.reviewed_pack))
    print("Applied reviewed pack")
    for key, value in summary.items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
