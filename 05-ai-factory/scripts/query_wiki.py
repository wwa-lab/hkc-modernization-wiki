"""Answer simple questions from the local HKC wiki.

This is a deterministic, standard-library-only query helper. It does not call
LLM APIs, use embeddings, start a server, read raw LAN folders, or use a
database. It searches `03-wiki/` and `07-references/source-document-index.json`
so an agent can answer with source pages and source materials.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "03-wiki"
WIKI_INDEX = WIKI / "index.md"
SOURCE_INDEX = ROOT / "07-references" / "source-document-index.json"


class WikiPage(NamedTuple):
    path: Path
    relative_path: str
    title: str
    content: str
    status: str
    confidence: str
    source_paths: tuple[str, ...]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def strip_frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content
    raw_frontmatter = content[4:end]
    body = content[end + 5 :].lstrip("\n")
    metadata: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, body


def first_heading(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def wiki_pages(root: Path = ROOT) -> list[WikiPage]:
    wiki_dir = root / "03-wiki"
    pages: list[WikiPage] = []
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.name == "index.md":
            continue
        content = path.read_text(encoding="utf-8")
        metadata, body = strip_frontmatter(content)
        relative = path.relative_to(wiki_dir).as_posix()
        pages.append(
            WikiPage(
                path=path,
                relative_path=relative,
                title=first_heading(body, path.stem.replace("-", " ").title()),
                content=body,
                status=metadata.get("status", content_status(body)),
                confidence=metadata.get("confidence", content_confidence(body)),
                source_paths=tuple(content_sources(body)),
            )
        )
    return pages


def content_status(content: str) -> str:
    if "Need Clarification" in content:
        return "Need Clarification"
    if "Conflict" in content:
        return "Conflict"
    if "SME Confirmed" in content:
        return "SME Confirmed"
    return "AI Organized"


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


def query_terms(query: str) -> set[str]:
    words = {word.lower() for word in re.findall(r"[A-Za-z0-9][A-Za-z0-9_.-]*", query)}
    return {word for word in words if len(word) >= 2 and word not in {"hkc", "wiki", "what", "the"}}


def score_page(page: WikiPage, terms: set[str]) -> int:
    if not terms:
        return 1 if page.source_paths else 0
    haystack = f"{page.relative_path}\n{page.title}\n{page.content}".lower()
    score = 0
    for term in terms:
        if term in haystack:
            score += haystack.count(term)
    if page.status in {"Need Clarification", "Conflict"}:
        score += 1
    return score


def relevant_pages(query: str, pages: list[WikiPage], limit: int) -> list[tuple[int, WikiPage]]:
    terms = query_terms(query)
    scored = [(score_page(page, terms), page) for page in pages]
    matches = [(score, page) for score, page in scored if score > 0]
    sorted_matches = sorted(matches, key=lambda item: (-item[0], item[1].relative_path))
    source_backed_matches = [
        (score, page) for score, page in sorted_matches if not is_meta_page(page) and page.source_paths
    ]
    knowledge_matches = [(score, page) for score, page in sorted_matches if not is_meta_page(page)]
    return (source_backed_matches or knowledge_matches or sorted_matches)[:limit]


def is_meta_page(page: WikiPage) -> bool:
    return page.relative_path == "log.md" or page.relative_path == "README.md" or page.relative_path.endswith("/README.md")


def extract_relevant_lines(page: WikiPage, terms: set[str], max_lines: int = 5) -> list[str]:
    lines: list[str] = []
    in_notes = False
    note_lines: list[str] = []
    for line in page.content.splitlines():
        stripped = line.strip()
        if stripped == "- Notes:":
            in_notes = True
            continue
        if in_notes and stripped.startswith("- ") and not stripped.startswith("- Notes:"):
            in_notes = False
        if in_notes and stripped.startswith("- "):
            candidate = stripped.removeprefix("- ").strip()
            lower = candidate.lower()
            if not terms or any(term in lower for term in terms):
                note_lines.append(candidate)
    if note_lines:
        return note_lines[:max_lines]

    for line in page.content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if any(
            stripped.startswith(prefix)
            for prefix in [
                "- Intake ID:",
                "- Material ID:",
                "- Status:",
                "- Review Status:",
                "- Confidence:",
                "- Evidence:",
                "- Optional SME Review Trigger:",
            ]
        ):
            continue
        if stripped.startswith("- source_path=") or stripped.startswith("- material_type="):
            continue
        candidate = stripped.removeprefix("- ").strip()
        if not candidate:
            continue
        lower = candidate.lower()
        if not terms or any(term in lower for term in terms):
            if candidate not in lines:
                lines.append(candidate)
        if len(lines) >= max_lines:
            break
    return lines


def source_index(root: Path = ROOT) -> list[dict[str, Any]]:
    path = root / "07-references" / "source-document-index.json"
    if not path.exists():
        return []
    data = load_json(path)
    return data if isinstance(data, list) else []


def source_materials_for_pages(pages: list[WikiPage], source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_paths = {source for page in pages for source in page.source_paths}
    rows = []
    for item in source_rows:
        if not isinstance(item, dict):
            continue
        if item.get("source_path") in source_paths:
            rows.append(item)
    return sorted(rows, key=lambda item: str(item.get("material_id", "")))


def answer_query(query: str, root: Path = ROOT, limit: int = 5) -> str:
    if not (root / "03-wiki" / "index.md").exists():
        raise FileNotFoundError("03-wiki/index.md is required before querying the wiki")
    pages = wiki_pages(root)
    matches = relevant_pages(query, pages, limit)
    matched_pages = [page for _, page in matches]
    rows = source_materials_for_pages(matched_pages, source_index(root))
    terms = query_terms(query)
    confidence = answer_confidence(matched_pages)

    lines = [
        "# Wiki Query Answer",
        "",
        f"- Query: {query}",
        "- Scope: `03-wiki/` and `07-references/source-document-index.json` only",
        f"- Confidence: {confidence}",
        "",
        "## Direct Answer",
        "",
    ]
    if not matched_pages:
        lines.extend(
            [
                "No matching wiki notes were found. Check whether the source has been ingested or whether the relevant page is still reference-only.",
                "",
            ]
        )
    else:
        for page in matched_pages:
            lines.append(f"- From `{page.relative_path}` ({page.status}, {page.confidence}):")
            relevant = extract_relevant_lines(page, terms)
            if relevant:
                lines.extend(f"  - {item}" for item in relevant)
            else:
                lines.append("  - Relevant page found, but no concise note line matched the query terms.")
        lines.append("")

    lines.extend(["## Source Pages", ""])
    if matched_pages:
        for page in matched_pages:
            lines.append(f"- `{page.relative_path}` - {page.status}, confidence {page.confidence}")
    else:
        lines.append("- None")
    lines.extend(["", "## Source Materials", ""])
    if rows:
        for row in rows:
            purpose = str(row.get("purpose", "")).strip()
            suffix = f" - {purpose}" if purpose else ""
            lines.append(
                f"- {row.get('material_id')}: `{row.get('source_path')}` "
                f"({row.get('wiki_status')}, {row.get('confidence')}){suffix}"
            )
    else:
        lines.append("- None found in source index for the matched pages.")

    question_pages = [page for page in matched_pages if "questions/" in page.relative_path]
    conflict_pages = [page for page in matched_pages if "conflict" in page.relative_path or page.status == "Conflict"]
    lines.extend(["", "## Open Questions / Conflicts", ""])
    if question_pages or conflict_pages:
        for page in question_pages:
            lines.append(f"- Open question source page: `{page.relative_path}`")
        for page in conflict_pages:
            lines.append(f"- Conflict source page: `{page.relative_path}`")
    else:
        lines.append("- None identified in matched wiki pages.")

    lines.extend(
        [
            "",
            "## Suggested Archive",
            "",
            "If this answer becomes durable after review, archive the synthesis as a new wiki page in the appropriate `03-wiki/` area.",
            "",
        ]
    )
    return "\n".join(lines)


def answer_confidence(pages: list[WikiPage]) -> str:
    if not pages:
        return "Low"
    if any(page.status in {"Need Clarification", "Conflict"} or page.confidence == "Low" for page in pages):
        return "Low"
    if all(page.confidence == "High" for page in pages):
        return "High"
    return "Medium"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local HKC wiki.")
    parser.add_argument("--query", required=True, help="Natural language question to answer from the wiki.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum matching wiki pages to include.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(answer_query(args.query, ROOT, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
