"""Subpacote de secoes: orquestradores e builders de front matter.

Cada secao Zola sincronizada (projects, events) tem:
- um builder de front matter (converte propriedades da Notion em dict/TOML),
- e usa o orquestrador base para percorrer paginas, fazer cache incremental,
  processar markdown (imagens + colunas) e escrever arquivos.
"""

from .base import sync_section, sync_single_page, find_page_by_slug, find_page_by_id
from .projects import build_project_front_matter
from .events import build_event_front_matter

__all__ = [
    "sync_section",
    "sync_single_page",
    "find_page_by_slug",
    "find_page_by_id",
    "build_project_front_matter",
    "build_event_front_matter",
]