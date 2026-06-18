"""Run the local Auto Wiki Intake flow.

This script is intentionally small and deterministic. It does not read real LAN
folders, call LLM APIs, parse RPG/BRD content, use Excel, use databases, or use
third-party packages. Intake JSON and optional inbox text files provide enough
mock material to prove the repo workflow.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AI_FACTORY = ROOT / "05-ai-factory"
DEFAULT_INBOX_PATH = AI_FACTORY / "inbox"
LATEST_AUTO_INTAKE_PATH = AI_FACTORY / "intake" / "latest-auto-intake.json"
WIKI = ROOT / "03-wiki"
REPORTS = ROOT / "06-reports"
REFERENCES = ROOT / "07-references"
SOURCE_INDEX_PATH = REFERENCES / "source-document-index.json"
LATEST_SUMMARY_PATH = REPORTS / "latest-intake-summary.md"
LATEST_INTAKE_REPORT_PATH = REPORTS / "latest-intake-report.md"
WIKI_INDEX_PATH = WIKI / "index.md"
WIKI_LOG_PATH = WIKI / "log.md"
OPEN_QUESTIONS_PATH = WIKI / "questions" / "open-questions.md"
CONFLICT_LOG_PATH = WIKI / "questions" / "conflict-log.md"

REQUIRED_INTAKE_FIELDS = [
    "intake_id",
    "project",
    "submitted_by",
    "submitted_date",
    "description",
    "materials",
]

STATUS_AI_ORGANIZED = "AI Organized"
OPTIONAL_REVIEW_STATUSES = {"Need Clarification", "Conflict"}

WIKI_TARGETS = {
    "overview": WIKI / "overview" / "program-notes.md",
    "legacy": WIKI / "legacy" / "file-notes.md",
    "batch": WIKI / "legacy" / "batch-flow-notes.md",
    "interface": WIKI / "legacy" / "interface-notes.md",
    "modernization": WIKI / "modernization" / "migration-patterns.md",
    "data": WIKI / "data" / "data-dictionary-notes.md",
    "field": WIKI / "data" / "field-meaning-notes.md",
    "code": WIKI / "data" / "code-value-notes.md",
}
FRONTMATTER_FIELDS = [
    "page_type",
    "domain",
    "status",
    "last_updated",
    "source_count",
    "confidence",
    "related_sources",
]
COMMON_UPPERCASE_WORDS = {
    "AS400",
    "CLLE",
    "HKC",
    "INBOX",
    "LAN",
    "DETAIL",
    "HEADER",
    "ORDER",
    "README",
    "RPGLE",
    "SOURCE",
    "TBD",
    "WIKI",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def read_text_if_repo_file(path_value: str) -> str:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def validate_intake(intake: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_INTAKE_FIELDS if not intake.get(field)]
    if missing:
        raise ValueError(f"Missing required intake field(s): {', '.join(missing)}")
    if not isinstance(intake["materials"], list) or not intake["materials"]:
        raise ValueError("intake.materials must be a non-empty list")
    seen_ids: set[str] = set()
    for index, material in enumerate(intake["materials"], start=1):
        if not isinstance(material, dict):
            raise ValueError(f"materials[{index}] must be an object")
        for field in ["material_id", "source_path", "material_type"]:
            if not material.get(field):
                raise ValueError(f"materials[{index}] missing required field: {field}")
        material_id = str(material["material_id"])
        if material_id in seen_ids:
            raise ValueError(f"Duplicate material_id: {material_id}")
        seen_ids.add(material_id)


def scan_inbox(inbox_dir: Path) -> list[dict[str, Any]]:
    if not inbox_dir.exists():
        return []
    materials: list[dict[str, Any]] = []
    inbox_files = sorted(item for item in inbox_dir.iterdir() if item.is_file() and item.name != "README.md")
    for index, path in enumerate(inbox_files, start=1):
        materials.append(
            {
                "material_id": f"INBOX-{index:03d}",
                "source_path": source_path_for_intake(path),
                "material_type": infer_material_type(path.name, path.read_text(encoding="utf-8")),
                "owner": "Inbox",
                "purpose": "Auto-discovered inbox material for local wiki intake.",
            }
        )
    return materials


def source_path_for_intake(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_intake(path: Path | None, inbox_dir: Path | None) -> dict[str, Any]:
    if path is not None:
        intake = load_json(path)
        if not isinstance(intake, dict):
            raise ValueError("Intake JSON must contain an object at the top level")
        if inbox_dir is not None:
            intake = {**intake, "materials": [*intake.get("materials", []), *scan_inbox(inbox_dir)]}
        return intake
    if inbox_dir is None:
        raise ValueError("Provide --intake or --inbox")
    return {
        "intake_id": f"INBOX-{date.today().isoformat()}",
        "project": "HKC Modernization",
        "submitted_by": "Agent intake",
        "submitted_date": date.today().isoformat(),
        "description": "Auto-generated intake from inbox files.",
        "materials": scan_inbox(inbox_dir),
    }


def material_ids(intake: dict[str, Any]) -> list[str]:
    return [str(material["material_id"]) for material in intake["materials"]]


def build_intake_from_request(
    request: str,
    inbox_dir: Path = DEFAULT_INBOX_PATH,
    source_paths: list[str] | None = None,
) -> dict[str, Any]:
    explicit_sources = [*extract_lan_paths(request), *(source_paths or [])]
    materials = request_source_materials(explicit_sources, request)
    if should_scan_inbox(request, explicit_sources):
        topic = request_topic(request)
        for material in scan_inbox(inbox_dir):
            material["purpose"] = f"Auto-discovered inbox material for {topic}."
            materials.append(material)
    if not materials:
        raise ValueError(
            "No source path was found and the inbox is empty. Add files to "
            "05-ai-factory/inbox or provide a LAN source path."
        )
    topic = request_topic(request)
    return {
        "intake_id": f"AUTO-{date.today().isoformat()}-{slugify(topic)}",
        "project": "HKC Modernization",
        "submitted_by": "Agent from user request",
        "submitted_date": date.today().isoformat(),
        "description": f"User requested Auto Wiki Intake for {topic}.",
        "request": request,
        "materials": materials,
    }


def extract_lan_paths(request: str) -> list[str]:
    quoted = re.findall(r"`([^`]*\\\\[^`]*)`", request)
    unquoted = re.findall(r"(\\\\[^\s，,。；;]+)", request)
    paths = quoted + [path for path in unquoted if path not in quoted]
    return sorted(dict.fromkeys(paths))


def request_source_materials(source_paths: list[str], request: str) -> list[dict[str, Any]]:
    materials: list[dict[str, Any]] = []
    for index, source_path in enumerate(source_paths, start=1):
        materials.append(
            {
                "material_id": f"REQ-SOURCE-{index:03d}",
                "source_path": source_path,
                "material_type": infer_material_type(source_path, request),
                "owner": "User request",
                "purpose": f"Source reference captured from natural language request: {request_topic(request)}.",
            }
        )
    return materials


def should_scan_inbox(request: str, explicit_sources: list[str]) -> bool:
    lowered = request.lower()
    return "inbox" in lowered or "收件" in lowered or "新资料" in lowered or not explicit_sources


def request_topic(request: str) -> str:
    cleaned = re.sub(r"`[^`]+`", " ", request)
    cleaned = re.sub(r"\\\\[^\s，,。；;]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "auto wiki intake"


def slugify(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value.upper())
    if not words:
        return "REQUEST"
    stop_words = {
        "AUTO",
        "HKC",
        "INBOX",
        "INTAKE",
        "TO",
        "WIKI",
        "THE",
        "UPDATE",
        "FROM",
        "WITH",
        "AND",
    }
    selected = [word for word in words if word not in stop_words][:6]
    return "-".join(selected or words[:6])


def infer_material_type(name: str, text: str) -> str:
    lowered = f"{name}\n{text}".lower()
    if "interface" in lowered or "api" in lowered or "ftp" in lowered:
        return "interface_note"
    if "batch" in lowered or "job" in lowered or "clle" in lowered:
        return "batch_flow_note"
    if "field" in lowered or "code value" in lowered or "data" in lowered:
        return "legacy_file_field_list"
    if "program" in lowered or "rpgle" in lowered or "screen" in lowered:
        return "legacy_summary_note"
    return "project_note"


def classify_material(material: dict[str, Any], text: str) -> dict[str, str]:
    material_type = str(material.get("material_type", "")).lower()
    combined = f"{material_type}\n{text}".lower()
    if "conflict" in combined or "contradict" in combined:
        return {"wiki_area": "questions", "topic": "conflict", "status": "Conflict", "confidence": "Low"}
    if "unknown" in combined or "tbd" in combined or "question" in combined:
        return {
            "wiki_area": "questions",
            "topic": "open_question",
            "status": "Need Clarification",
            "confidence": "Low",
        }
    if "field" in material_type or "data" in combined:
        return {"wiki_area": "data", "topic": "field", "status": STATUS_AI_ORGANIZED, "confidence": "Medium"}
    if "code value" in combined:
        return {"wiki_area": "data", "topic": "code", "status": STATUS_AI_ORGANIZED, "confidence": "Medium"}
    if "batch" in material_type or "job" in combined:
        return {"wiki_area": "legacy", "topic": "batch", "status": STATUS_AI_ORGANIZED, "confidence": "Medium"}
    if "interface" in material_type:
        return {"wiki_area": "legacy", "topic": "interface", "status": STATUS_AI_ORGANIZED, "confidence": "Medium"}
    if "modernization" in combined or "migration" in combined:
        return {
            "wiki_area": "modernization",
            "topic": "modernization",
            "status": STATUS_AI_ORGANIZED,
            "confidence": "Medium",
        }
    if "legacy" in material_type or "program" in combined:
        return {"wiki_area": "legacy", "topic": "overview", "status": STATUS_AI_ORGANIZED, "confidence": "Medium"}
    return {"wiki_area": "overview", "topic": "overview", "status": STATUS_AI_ORGANIZED, "confidence": "Medium"}


def summarize_material(material: dict[str, Any], text: str) -> list[str]:
    purpose = str(material.get("purpose", "")).strip()
    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    if purpose:
        lines.insert(0, purpose)
    concise = []
    for line in lines:
        if line.startswith("#"):
            continue
        concise.append(apply_wikilinks(line[:220]))
        if len(concise) == 3:
            break
    if not concise:
        concise.append("Material registered for wiki intake; source content remains in LAN folder or inbox reference.")
    return concise


def apply_wikilinks(text: str) -> str:
    """Add lightweight wikilinks around likely legacy object names."""
    result = []
    index = 0
    while index < len(text):
        if text.startswith("[[", index):
            end = text.find("]]", index)
            if end != -1:
                result.append(text[index : end + 2])
                index = end + 2
                continue
        char = text[index]
        if char.isupper() or char.isdigit():
            start = index
            while index < len(text) and (text[index].isupper() or text[index].isdigit() or text[index] == "."):
                index += 1
            raw_token = text[start:index]
            token = raw_token.rstrip(".")
            suffix = raw_token[len(token) :]
            if should_wikilink(token):
                result.append(f"[[{token}]]{suffix}")
            else:
                result.append(raw_token)
            continue
        result.append(char)
        index += 1
    return "".join(result)


def should_wikilink(token: str) -> bool:
    if len(token) < 4:
        return False
    if token in COMMON_UPPERCASE_WORDS:
        return False
    if token.startswith(("MAT", "WIKI-MAT", "INBOX-")):
        return False
    return any(char.isalpha() for char in token)


def extract_wiki_notes(intake: dict[str, Any]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for material in intake["materials"]:
        text = read_text_if_repo_file(str(material["source_path"]))
        classification = classify_material(material, text)
        note = {
            "intake_id": intake["intake_id"],
            "material_id": material["material_id"],
            "source_path": material["source_path"],
            "material_type": material["material_type"],
            "wiki_area": classification["wiki_area"],
            "topic": classification["topic"],
            "status": classification["status"],
            "confidence": classification["confidence"],
            "evidence": [f"source_path={material['source_path']}", f"material_type={material['material_type']}"],
            "notes": summarize_material(material, text),
        }
        notes.append(note)
    return notes


def note_target(note: dict[str, Any]) -> Path:
    if note["status"] == "Conflict":
        return CONFLICT_LOG_PATH
    if note["status"] == "Need Clarification":
        return OPEN_QUESTIONS_PATH
    return WIKI_TARGETS.get(str(note["topic"]), WIKI_TARGETS["overview"])


def append_block(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    else:
        existing = f"# {title}\n\n"
        path.write_text(existing, encoding="utf-8", newline="\n")
    block_id = next((line for line in lines if line.startswith("- Material ID:")), "")
    if block_id and block_id in existing:
        return
    with path.open("a", encoding="utf-8", newline="\n") as file:
        if existing and not existing.endswith("\n\n"):
            file.write("\n")
        file.write("\n".join(lines))
        file.write("\n")


def render_note_block(note: dict[str, Any]) -> list[str]:
    lines = [
        f"## {note['material_id']} - {note['material_type']}",
        "",
        f"- Intake ID: {note['intake_id']}",
        f"- Material ID: {note['material_id']}",
        f"- Source: `{note['source_path']}`",
        f"- Status: {note['status']}",
        f"- Review Status: {note['status']}",
        f"- Confidence: {note['confidence']}",
        "- Evidence:",
    ]
    lines.extend(f"  - {item}" for item in note["evidence"])
    lines.append("- Notes:")
    lines.extend(f"  - {item}" for item in note["notes"])
    if note["status"] in OPTIONAL_REVIEW_STATUSES:
        lines.append("- Optional SME Review Trigger: Yes")
    else:
        lines.append("- Optional SME Review Trigger: No")
    lines.append("")
    return lines


def update_wiki(notes: list[dict[str, Any]]) -> None:
    titles = {
        OPEN_QUESTIONS_PATH: "Open Questions",
        CONFLICT_LOG_PATH: "Conflict Log",
    }
    for note in notes:
        target = note_target(note)
        title = titles.get(target, target.stem.replace("-", " ").title())
        append_block(target, title, render_note_block(note))
    ensure_wiki_frontmatter()
    ensure_review_status_labels()
    ensure_note_wikilinks()


def markdown_files() -> list[Path]:
    return sorted(path for path in WIKI.rglob("*.md") if ".git" not in path.parts)


def read_without_frontmatter(path: Path) -> str:
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    if not content.startswith("---\n"):
        return content
    end = content.find("\n---\n", 4)
    if end == -1:
        return content
    return content[end + 5 :].lstrip("\n")


def page_domain(path: Path) -> str:
    relative = path.relative_to(WIKI)
    return relative.parts[0] if len(relative.parts) > 1 else "wiki"


def page_type(path: Path) -> str:
    if path == WIKI_INDEX_PATH:
        return "index"
    if path == WIKI_LOG_PATH:
        return "log"
    if path.name == "README.md":
        return "readme"
    if path.parent.name == "questions":
        return "question-log"
    return path.stem


def content_status(content: str, fallback: str = STATUS_AI_ORGANIZED) -> str:
    if "- Review Status: Conflict" in content or "- Status: Conflict" in content:
        return "Conflict"
    if "- Review Status: Need Clarification" in content or "- Status: Need Clarification" in content:
        return "Need Clarification"
    if "- Review Status: SME Confirmed" in content or "- Status: SME Confirmed" in content:
        return "SME Confirmed"
    if "- Review Status: AI Organized" in content or "- Status: AI Organized" in content:
        return STATUS_AI_ORGANIZED
    return fallback


def content_confidence(content: str) -> str:
    if "- Confidence: Low" in content:
        return "Low"
    if "- Confidence: High" in content:
        return "High"
    return "Medium"


def content_sources(content: str) -> list[str]:
    sources: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Source:"):
            sources.append(stripped.removeprefix("- Source:").strip().strip("`"))
        if "source_path=" in stripped:
            sources.append(stripped.split("source_path=", 1)[1].strip().strip("`"))
    return sorted(set(item for item in sources if item))


def render_frontmatter(path: Path, content: str, status: str | None = None) -> str:
    sources = content_sources(content)
    fields = {
        "page_type": page_type(path),
        "domain": page_domain(path),
        "status": status or content_status(content),
        "last_updated": date.today().isoformat(),
        "source_count": str(len(sources)),
        "confidence": content_confidence(content),
        "related_sources": "[" + ", ".join(json.dumps(source) for source in sources) + "]",
    }
    lines = ["---"]
    lines.extend(f"{field}: {fields[field]}" for field in FRONTMATTER_FIELDS)
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def ensure_wiki_frontmatter() -> None:
    for path in markdown_files():
        content = read_without_frontmatter(path)
        if path == WIKI_LOG_PATH and path.exists() and path.read_text(encoding="utf-8").startswith("---\n"):
            continue
        path.write_text(render_frontmatter(path, content) + content.lstrip("\n"), encoding="utf-8", newline="\n")


def ensure_review_status_labels() -> None:
    for path in markdown_files():
        content = path.read_text(encoding="utf-8")
        if "- Status:" not in content:
            continue
        lines = content.splitlines()
        updated: list[str] = []
        for index, line in enumerate(lines):
            updated.append(line)
            if line.startswith("- Status:"):
                next_line = lines[index + 1] if index + 1 < len(lines) else ""
                if not next_line.startswith("- Review Status:"):
                    updated.append("- Review Status:" + line.split(":", 1)[1])
        path.write_text("\n".join(updated) + "\n", encoding="utf-8", newline="\n")


def ensure_note_wikilinks() -> None:
    for path in markdown_files():
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        updated: list[str] = []
        in_notes = False
        for line in lines:
            if line == "- Notes:":
                in_notes = True
                updated.append(line)
                continue
            if in_notes and line.startswith("- "):
                in_notes = False
            if in_notes and line.startswith("  - "):
                updated.append("  - " + apply_wikilinks(line.removeprefix("  - ")))
            else:
                updated.append(line)
        path.write_text("\n".join(updated) + "\n", encoding="utf-8", newline="\n")


def first_heading(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def render_wiki_index() -> str:
    rows = []
    for path in markdown_files():
        if path == WIKI_INDEX_PATH:
            continue
        content = read_without_frontmatter(path)
        relative = path.relative_to(WIKI).as_posix()
        title = first_heading(content, path.stem.replace("-", " ").title())
        status = content_status(content)
        source_count = len(content_sources(content))
        rows.append((relative, title, status, date.today().isoformat(), source_count))
    lines = [
        "# Wiki Index",
        "",
        "Navigation entry for LLM agents and human readers. Read this page before querying or updating the wiki.",
        "",
        "| Page | Purpose | Status | Last Updated | Source Count |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| [[{relative.removesuffix('.md')}]] | {title} | {status} | {updated} | {source_count} |"
        for relative, title, status, updated, source_count in rows
    )
    lines.append("")
    return render_frontmatter(WIKI_INDEX_PATH, "\n".join(lines), STATUS_AI_ORGANIZED) + "\n".join(lines) + "\n"


def update_wiki_index() -> None:
    WIKI_INDEX_PATH.write_text(render_wiki_index(), encoding="utf-8", newline="\n")


def ensure_wiki_log() -> None:
    if WIKI_LOG_PATH.exists():
        return
    body = "# Wiki Operation Log\n\nAppend-only operation log for ingest, query, and lint activity.\n\n"
    WIKI_LOG_PATH.write_text(render_frontmatter(WIKI_LOG_PATH, body, STATUS_AI_ORGANIZED) + body, encoding="utf-8", newline="\n")


def append_wiki_log(intake: dict[str, Any], notes: list[dict[str, Any]]) -> None:
    ensure_wiki_log()
    updated_pages = sorted({note_target(note).relative_to(WIKI).as_posix() for note in notes})
    open_questions = [str(note["material_id"]) for note in notes if note["status"] == "Need Clarification"]
    conflicts = [str(note["material_id"]) for note in notes if note["status"] == "Conflict"]
    lines = [
        f"## [{date.today().isoformat()}] ingest | {intake['intake_id']}",
        "- Sources:",
    ]
    for material in intake["materials"]:
        lines.append(f"  - {material['material_id']}: `{material['source_path']}`")
    lines.append("- Pages updated:")
    for page in updated_pages:
        lines.append(f"  - [[{page.removesuffix('.md')}]]")
    lines.append("- Open questions:")
    lines.extend(f"  - {item}" for item in open_questions) if open_questions else lines.append("  - None")
    lines.append("- Conflicts:")
    lines.extend(f"  - {item}" for item in conflicts) if conflicts else lines.append("  - None")
    lines.append("")
    with WIKI_LOG_PATH.open("a", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines))
        file.write("\n")


def update_source_index(intake: dict[str, Any], notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = load_json(SOURCE_INDEX_PATH) if SOURCE_INDEX_PATH.exists() else []
    if not isinstance(existing, list):
        existing = []
    current_material_ids = {str(material["material_id"]) for material in intake["materials"]}
    by_id = {
        str(item.get("material_id")): item
        for item in existing
        if isinstance(item, dict)
        and not (
            item.get("intake_id") == intake["intake_id"]
            and str(item.get("material_id")) not in current_material_ids
        )
    }
    note_by_id = {str(note["material_id"]): note for note in notes}
    for material in intake["materials"]:
        material_id = str(material["material_id"])
        note = note_by_id[material_id]
        by_id[material_id] = {
            "material_id": material_id,
            "source_path": material["source_path"],
            "material_type": material["material_type"],
            "owner": material.get("owner", "Unknown"),
            "purpose": material.get("purpose", ""),
            "intake_id": intake["intake_id"],
            "wiki_area": note["wiki_area"],
            "wiki_status": note["status"],
            "confidence": note["confidence"],
            "last_indexed": date.today().isoformat(),
        }
    updated = sorted(by_id.values(), key=lambda item: str(item.get("material_id", "")))
    write_json(SOURCE_INDEX_PATH, updated)
    return updated


def build_candidates(intake: dict[str, Any]) -> dict[str, Any]:
    """Build optional SME review candidates for selective review only."""
    sources = material_ids(intake)
    return {
        "intake_id": intake["intake_id"],
        "project": intake["project"],
        "created_from": "mock extraction for optional selective SME review",
        "default_workflow": "Auto Wiki Intake",
        "candidates": [
            {
                "item_id": "SME-ITEM-001",
                "type": "Program Review",
                "legacy_object": "ORDENTR",
                "ai_recommended_answer": (
                    "`ORDENTR` appears to be an order entry program used to "
                    "create or maintain customer orders."
                ),
                "why_ai_recommends_this": (
                    "The program name resembles order entry, and the mock "
                    "evidence references order header and detail file usage."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-002",
                    "Observed terms: ORDER HEADER, ORDER DETAIL, ENTRY SCREEN",
                ],
                "confidence": "Medium",
                "alternative_answers": [
                    "Order inquiry screen program.",
                    "Batch order validation program.",
                    "Order maintenance program.",
                ],
                "question_for_sme": "What is the best legacy iSeries description of program `ORDENTR`?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": STATUS_AI_ORGANIZED,
            },
            {
                "item_id": "SME-ITEM-002",
                "type": "Field Review",
                "legacy_object": "CUSTNO",
                "ai_recommended_answer": (
                    "`CUSTNO` is the customer number field used to identify "
                    "the customer associated with an order or account record."
                ),
                "why_ai_recommends_this": (
                    "The field name resembles customer number, and the mock "
                    "evidence places it near customer and order records."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-001",
                    "Observed terms: CUSTOMER FILE, ORDER HEADER, CUSTNO",
                ],
                "confidence": "High",
                "alternative_answers": [
                    "Billing customer number.",
                    "Ship-to customer number.",
                    "Customer account number used only for reporting.",
                ],
                "question_for_sme": "What is the correct legacy meaning of field `CUSTNO`?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": STATUS_AI_ORGANIZED,
            },
            {
                "item_id": "SME-ITEM-003",
                "type": "Program Review",
                "legacy_object": "PRCADJ",
                "ai_recommended_answer": (
                    "`PRCADJ` may be a pricing adjustment program, but the "
                    "available mock evidence is incomplete."
                ),
                "why_ai_recommends_this": (
                    "The name suggests price adjustment, yet the mock source "
                    "does not show enough business context."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-002",
                    "Observed terms: PRICE, ADJUST, MANUAL OVERRIDE",
                ],
                "confidence": "Low",
                "alternative_answers": [
                    "Promotion adjustment program.",
                    "Manual price override screen.",
                    "Obsolete pricing batch utility.",
                ],
                "question_for_sme": "Does `PRCADJ` require a legacy business discussion before confirmation?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": "Need Clarification",
            },
            {
                "item_id": "SME-ITEM-004",
                "type": "Field Review",
                "legacy_object": "TMPFLAG",
                "ai_recommended_answer": (
                    "`TMPFLAG` appears to be a temporary processing flag and "
                    "may not represent stable business meaning."
                ),
                "why_ai_recommends_this": (
                    "The mock evidence only shows temporary work-file usage, "
                    "not a persistent business field."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-001",
                    "Observed terms: WORK FILE, TEMP, TMPFLAG",
                ],
                "confidence": "Low",
                "alternative_answers": [
                    "Internal batch retry flag.",
                    "Temporary UI state flag.",
                    "Obsolete migration-only field.",
                ],
                "question_for_sme": "Should `TMPFLAG` be excluded from confirmed legacy field knowledge?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": "Need Clarification",
            },
        ],
    }


def write_optional_candidates(intake: dict[str, Any]) -> Path:
    candidate_pack = build_candidates(intake)
    output_path = AI_FACTORY / "logs" / f"{intake['intake_id']}-candidates.json"
    write_json(output_path, candidate_pack)
    return output_path


def render_summary(intake: dict[str, Any], notes: list[dict[str, Any]], source_index_count: int) -> str:
    review_needed = [note for note in notes if note["status"] in OPTIONAL_REVIEW_STATUSES or note["confidence"] == "Low"]
    lines = [
        f"# Latest Intake Summary - {intake['intake_id']}",
        "",
        f"- Project: {intake['project']}",
        f"- Submitted By: {intake['submitted_by']}",
        f"- Submitted Date: {intake['submitted_date']}",
        "- Default Workflow: Auto Wiki Intake",
        "- Default AI Status: AI Organized",
        f"- Materials Processed: {len(notes)}",
        f"- Source Index Entries: {source_index_count}",
        f"- Optional SME Review Items: {len(review_needed)}",
        "",
        "## Main Workflow",
        "",
        "Materials/LAN references/inbox files -> Agent intake -> Auto classification -> Wiki update -> Source index update -> Open questions/conflict log -> Intake summary -> Optional SME review only when needed.",
        "",
        "## Wiki Updates",
        "",
    ]
    for note in notes:
        lines.append(
            f"- {note['material_id']}: {note['wiki_area']} / {note['topic']} / {note['status']} / {note['confidence']}"
        )
    lines.extend(["", "## Optional SME Review Triggers", ""])
    if review_needed:
        for note in review_needed:
            lines.append(f"- {note['material_id']}: {note['status']} ({note['confidence']})")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Constraints",
            "",
            "- Python standard library only.",
            "- Markdown for wiki and reports.",
            "- JSON for metadata, dictionaries, and indexes.",
            "- LAN folder remains the raw document source of truth.",
            "- AI-generated content must not be marked SME Confirmed without explicit SME confirmation.",
            "",
        ]
    )
    return "\n".join(lines)


def write_summary(intake: dict[str, Any], notes: list[dict[str, Any]], source_index_count: int) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    summary = render_summary(intake, notes, source_index_count)
    LATEST_SUMMARY_PATH.write_text(summary, encoding="utf-8", newline="\n")
    LATEST_INTAKE_REPORT_PATH.write_text(summary, encoding="utf-8", newline="\n")


def process_intake(intake: dict[str, Any]) -> dict[str, Any]:
    validate_intake(intake)
    notes = extract_wiki_notes(intake)
    update_wiki(notes)
    source_index = update_source_index(intake, notes)
    append_wiki_log(intake, notes)
    update_wiki_index()
    candidates_path = write_optional_candidates(intake)
    write_summary(intake, notes, len(source_index))
    return {
        "intake_id": intake["intake_id"],
        "materials_processed": len(notes),
        "source_index_entries": len(source_index),
        "optional_candidates_path": str(candidates_path),
        "summary_path": str(LATEST_SUMMARY_PATH),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process intake JSON or inbox files into wiki notes.")
    parser.add_argument("--intake", help="Path to intake JSON.")
    parser.add_argument("--inbox", help="Optional inbox directory to scan.")
    parser.add_argument("--request", help="Natural language request to turn into latest-auto-intake.json.")
    parser.add_argument("--source", action="append", default=[], help="Optional LAN/source path for --request.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generated_intake_path = ""
    if args.request:
        inbox_dir = Path(args.inbox) if args.inbox else DEFAULT_INBOX_PATH
        intake = build_intake_from_request(args.request, inbox_dir, args.source)
        write_json(LATEST_AUTO_INTAKE_PATH, intake)
        generated_intake_path = str(LATEST_AUTO_INTAKE_PATH)
    else:
        intake_path = Path(args.intake) if args.intake else None
        inbox_dir = Path(args.inbox) if args.inbox else None
        intake = load_intake(intake_path, inbox_dir)
    result = process_intake(intake)
    if generated_intake_path:
        print(f"Wrote generated intake: {generated_intake_path}")
    print(f"Processed intake: {result['intake_id']}")
    print(f"Materials processed: {result['materials_processed']}")
    print(f"Source index entries: {result['source_index_entries']}")
    print(f"Wrote optional SME candidates: {result['optional_candidates_path']}")
    print(f"Wrote intake summary: {result['summary_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
