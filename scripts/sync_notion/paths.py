"""Paths e constantes fixas do sync.

Modulo isolado para evitar ciclos de importacao: `config` e `sections.base`
precisam dos paths, mas `config` tambem importa `sections` (para os builders),
entao separamos o que e puramente de filesystem aqui.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_ROOT = REPO_ROOT / "content"
STATIC_ROOT = REPO_ROOT / "static"

# Onde as imagens baixadas da Notion sao salvas.
# Resulta em static/notion/images/{section}/{slug}/<arquivo>.
IMAGES_ROOT = STATIC_ROOT / "notion" / "images"

# Prefixo web usado no markdown para referenciar as imagens baixadas.
IMAGES_WEB_PREFIX = "/notion/images"

# Arquivo de cache dos assets baixados (url -> path local + sha256).
CACHE_FILE = STATIC_ROOT / "notion" / ".cache.json"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"