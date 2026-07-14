"""Sync Notion databases to Zola content files.

Run with:
    source .env && python scripts/sync_notion.py

Expected .env exports:
    export NOTION_TOKEN=secret_xxx
    export NOTION_PROJECTS_DB_ID=...
    export NOTION_EVENTS_DB_ID=...
"""

import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent

API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2026-03-11",
    "Content-Type": "application/json",
}

CONTENT_ROOT = Path(__file__).parent.parent / "content"


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing environment variable: {name}")
    return value


def fetch_json(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(method, f"{API}{path}", headers=HEADERS, **kwargs)
    resp.raise_for_status()
    return resp.json()


def get_data_source_id(database_id: str) -> str:
    """Resolve the first data source id for a database."""
    db = fetch_json("GET", f"/databases/{database_id}")
    sources = db.get("data_sources", [])
    if not sources:
        raise SystemExit(f"Database {database_id} has no data_sources")
    return sources[0]["id"]


def query_data_source(data_source_id: str, start_cursor: str | None = None) -> dict:
    body = {
        "filter": {"property": "Publicar", "checkbox": {"equals": True}},
        "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
    }
    if start_cursor:
        body["start_cursor"] = start_cursor
    return fetch_json("POST", f"/data_sources/{data_source_id}/query", json=body)


def all_pages(data_source_id: str) -> list[dict]:
    pages: list[dict] = []
    cursor: str | None = None
    while True:
        data = query_data_source(data_source_id, cursor)
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return pages


def plain_text(value: dict | None) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return "".join(
            part.get("plain_text", part.get("text", {}).get("content", ""))
            for part in value
        )
    if isinstance(value, dict):
        return value.get("plain_text", value.get("text", {}).get("content", ""))
    return str(value)


def rich_text(prop: dict) -> str:
    return plain_text(prop.get("rich_text", [])).strip()


def multi_select_names(prop: dict) -> list[str]:
    return [opt["name"] for opt in prop.get("multi_select", [])]


def select_name(prop: dict) -> str:
    sel = prop.get("select")
    return sel["name"] if sel else ""


def url_value(prop: dict) -> str:
    return prop.get("url") or ""


def date_value(prop: dict) -> str | None:
    d = prop.get("date")
    if not d:
        return None
    return d.get("start") or None


def checkbox_value(prop: dict) -> bool:
    return bool(prop.get("checkbox", False))


def title_text(props: dict) -> str:
    return plain_text(props.get("Nome", {}).get("title", [])).strip()


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def fetch_markdown(page_id: str) -> str:
    data = fetch_json("GET", f"/pages/{page_id}/markdown")
    return data.get("markdown", "")


def strip_metadata_markdown(markdown: str) -> str:
    """Remove bold metadata lines at the top of the markdown body."""
    lines = markdown.splitlines()
    metadata_keys = (
        "Status:",
        "Data:",
        "Início:",
        "Tags:",
        "Parceiros:",
        "Destaque:",
        "Local:",
        "Público:",
        "Link externo:",
    )
    while lines and any(lines[0].strip().startswith(f"**{key}") for key in metadata_keys):
        lines.pop(0)
    return "\n".join(lines).strip()


def build_project_front_matter(page: dict, slug: str, markdown: str) -> str:
    props = page["properties"]
    tags = multi_select_names(props.get("Tags", {}))
    external_link = url_value(props.get("Link externo", {}))
    start_date = date_value(props.get("Início", {}))

    extra = {
        "status": select_name(props.get("Status", {})),
        "tags": tags,
        "partners": rich_text(props.get("Parceiros", {})),
        "highlight": checkbox_value(props.get("Destacado", {})),
        "external_link": external_link,
    }
    if start_date is None:
        extra["start_date"] = ""
    else:
        extra["start_date"] = start_date

    fm: dict = {
        "title": title_text(props),
        "description": rich_text(props.get("Destaque", {})),
        "weight": 10,
        "draft": False,
        "extra": extra,
    }
    # Only add top-level Zola date if the project has an actual start date.
    if start_date is not None:
        fm["date"] = start_date

    return dumps_front_matter(fm) + "\n\n" + strip_metadata_markdown(markdown)


def build_event_front_matter(page: dict, slug: str, markdown: str) -> str:
    props = page["properties"]
    tags = multi_select_names(props.get("Tags", {}))
    external_link = url_value(props.get("Link externo", {}))
    event_date = date_value(props.get("Data", {}))

    extra = {
        "status": select_name(props.get("Status", {})),
        "tags": tags,
        "location": rich_text(props.get("Local", {})),
        "audience": rich_text(props.get("Público", {})),
        "partners": rich_text(props.get("Parceiros", {})),
        "highlight": checkbox_value(props.get("Destacado", {})),
        "external_link": external_link,
    }

    if event_date is None:
        extra["date_text"] = "Data a marcar"

    fm: dict = {
        "title": title_text(props),
        "description": rich_text(props.get("Destaque", {})) or select_name(props.get("Status", {})),
        "draft": False,
        "extra": extra,
    }
    # Use the real date when available; otherwise pin to the far future so
    # TBA items show up at the end (or swap to a different sentinel if desired).
    fm["date"] = event_date if event_date is not None else "2099-12-31"

    return dumps_front_matter(fm) + "\n\n" + strip_metadata_markdown(markdown)


def dumps_front_matter(obj: dict) -> str:
    """Dump a dict to Zola/TOML front matter."""
    lines = ["+++"]

    def _escape(value) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)):
            return str(value)
        if value is None or value == "":
            return '""'
        text = str(value)
        if isinstance(value, list):
            if not text:
                return "[]"
            return "[" + ", ".join(_escape(item) for item in value) + "]"
        text = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{text}"'

    def _write_table(table: dict, path: str = "") -> None:
        scalars = []
        nested = []
        for key, value in table.items():
            if isinstance(value, dict):
                nested.append((key, value))
            else:
                scalars.append((key, value))

        # Top-level scalars first, then nested tables.
        if path:
            lines.append(f"[{path}]")
        for key, value in scalars:
            lines.append(f"{key} = {_escape(value)}")
        if path and (scalars or not nested):
            lines.append("")

        for key, value in nested:
            subpath = f"{path}.{key}" if path else key
            _write_table(value, subpath)

    _write_table(obj)
    lines.append("+++")
    return "\n".join(lines).rstrip() + "\n"


def parse_notion_time(value: str) -> datetime:
    """Parse an ISO 8601 timestamp from Notion into an aware UTC datetime."""
    value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def file_mtime(path: Path) -> datetime | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def sync_section(
    database_id: str,
    section_dir: Path,
    builder,
) -> None:
    print(f"Syncing {section_dir.name}...")
    data_source_id = get_data_source_id(database_id)
    pages = all_pages(data_source_id)
    print(f"  {len(pages)} publishable pages found")

    section_dir.mkdir(parents=True, exist_ok=True)

    published_slugs: set[str] = set()
    written = 0
    skipped = 0

    for page in pages:
        title = title_text(page["properties"])
        slug = slugify(title)
        page_id = page["id"]
        published_slugs.add(slug)

        target = section_dir / f"{slug}.md"
        last_edited = parse_notion_time(page["last_edited_time"])
        mtime = file_mtime(target)

        if mtime and mtime >= last_edited:
            skipped += 1
            print(f"  up-to-date {section_dir.name}/{slug}.md")
            continue

        markdown = fetch_markdown(page_id)
        content = builder(page, slug, markdown)
        target.write_text(content, encoding="utf-8")
        # Preserve the Notion edit time as the file mtime so subsequent runs skip it.
        os.utime(target, (last_edited.timestamp(), last_edited.timestamp()))
        written += 1
        print(f"  wrote {section_dir.name}/{slug}.md")

    # Remove generated files that no longer exist in Notion (or are unpublished).
    removed = 0
    for path in section_dir.glob("*.md"):
        if path.name == "_index.md":
            continue
        slug = path.stem
        if slug not in published_slugs:
            path.unlink()
            removed += 1
            print(f"  removed {section_dir.name}/{path.name}")

    print(f"  {written} written, {skipped} up-to-date, {removed} removed")


def main() -> None:
    projects_db = get_env("NOTION_PROJECTS_DB_ID")
    events_db = get_env("NOTION_EVENTS_DB_ID")

    sync_section(projects_db, CONTENT_ROOT / "projects", build_project_front_matter)
    sync_section(events_db, CONTENT_ROOT / "events", build_event_front_matter)

    print("Done.")


if __name__ == "__main__":
    main()
