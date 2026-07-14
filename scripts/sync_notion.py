import json
import os
import re
from datetime import datetime

import requests

# Exporte as variáveis antes de rodar:
#   source .env && python scripts/sync_notion.py
API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2026-03-11",
}
INDEX_ID = os.environ["NOTION_INDEX_ID"]


def fetch_page(page_id: str) -> dict:
    """Fetch Notion page metadata (includes last_edited_time)."""
    resp = requests.get(f"{API}/pages/{page_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def fetch_page_markdown(page_id: str) -> dict:
    """Fetch a Notion page's markdown export."""
    resp = requests.get(f"{API}/pages/{page_id}/markdown", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def parse_index(markdown: str) -> list[str]:
    """Extract linked page UUIDs from the index page markdown.

    Notion renders links as `https://app.notion.com/p/{32-char-hex}`.
    """
    return re.findall(r"https://app\.notion\.com/p/([a-f0-9]{32})", markdown)


def main():
    # 1. Puxa o índice (leve, rápido) e metadados para cache
    index_md = fetch_page_markdown(INDEX_ID)
    index_meta = fetch_page(INDEX_ID)
    markdown = index_md["markdown"]
    last_edited = datetime.fromisoformat(index_meta["last_edited_time"])

    # 2. Parseia a tabela com regex — extrai page_id de cada link
    page_ids = parse_index(markdown)

    # 3. Cache: se last_edited do índice não mudou, nada mudou. Skip.
    cached_date: datetime | None = None
    cached_content: dict | None = None
    if cached_date == last_edited:
        return cached_content

    # 4. Puxa cada página individual (só o que mudou ou precisa renderizar)
    pages = {}
    for pid in page_ids:
        page = fetch_page_markdown(pid)
        content = page["markdown"]
        # parse: **Tags:** ..., **Data:** ..., **Status:** ..., resto é copy
        # TODO: implement front-matter / body extraction here.
        pages[pid] = {
            "markdown": content,
            "last_edited": page.get("last_edited_time"),
        }

    return pages


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, default=str))
