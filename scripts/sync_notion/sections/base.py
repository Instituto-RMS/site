"""Orquestrador de sync por secao.

Responsavel por:
- Consultar paginas publicaveis no data source da Notion.
- Aplicar cache incremental por mtime (so reescreve o que mudou).
- Instanciar o AssetDownloader contextualizado por secao/slug.
- Renderizar markdown final (imagens baixadas + colunas convertidas).
- Escrever o .md em content/{section}/{slug}.md.
- Remover arquivos que nao existem mais no Notion (no sync completo).

Tambem expoe o fluxo de sync de uma pagina so (debug/dev), que reusa o
mesmo pipeline mas sem limpeza de arquivos antigos.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

from ..cache import AssetCache
from ..markdown.renderer import render_markdown
from ..markdown.transforms import parse_notion_time, slugify, title_text
from ..models import Page, SectionConfig, SyncStats
from ..notion_client import NotionClient
from ..paths import CACHE_FILE, IMAGES_ROOT, IMAGES_WEB_PREFIX

log = logging.getLogger(__name__)


# --- helpers compartilhados ---------------------------------------------------

def _file_mtime(path: Path) -> Optional[datetime]:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _make_downloader(
    section: SectionConfig, slug: str, cache: AssetCache, *, download: bool
):
    from ..assets import AssetDownloader

    return AssetDownloader(
        images_root=IMAGES_ROOT,
        web_prefix=IMAGES_WEB_PREFIX,
        section=section.name,
        slug=slug,
        cache=cache,
        download=download,
    )


def _process_page(
    page: dict,
    section: SectionConfig,
    client: NotionClient,
    cache: AssetCache,
    *,
    download_assets: bool,
) -> tuple[bool, int]:
    """Processa uma pagina: baixa markdown, renderiza e escreve .md.

    Retorna (escreveu, n_assets_baixados). `escreveu=False` significa que
    o arquivo local ja estava atualizado (cache incremental por mtime).
    """

    props = page["properties"]
    title = title_text(props)
    slug = slugify(title)

    target = section.section_dir / f"{slug}.md"
    last_edited = parse_notion_time(page["last_edited_time"])
    mtime = _file_mtime(target)

    if mtime and mtime >= last_edited:
        log.info("up-to-date %s/%s.md", section.name, slug)
        return False, 0

    markdown = client.fetch_markdown(page["id"])
    downloader = _make_downloader(
        section, slug, cache, download=download_assets
    )
    body = render_markdown(markdown, asset_downloader=downloader)
    content = section.build_front_matter(page, slug, body)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    # Preserva o last_edited_time da Notion como mtime do arquivo: proxima
    # execucao vai pular se nada mudou no Notion.
    os.utime(target, (last_edited.timestamp(), last_edited.timestamp()))
    log.info("wrote %s/%s.md", section.name, slug)
    return True, 0  # n_assets poderia vir do downloader; mantemos simples.


# --- sync completo ------------------------------------------------------------

def sync_section(
    section: SectionConfig,
    client: NotionClient,
    *,
    download_assets: bool = True,
) -> SyncStats:
    """Sincroniza todos os itens publicaveis de uma secao."""

    log.info("Syncing %s...", section.name)
    data_source_id = client.get_data_source_id(section.database_id)
    pages = client.all_pages(data_source_id)
    log.info("  %d publishable pages found", len(pages))

    section.section_dir.mkdir(parents=True, exist_ok=True)
    cache = AssetCache(CACHE_FILE)

    stats = SyncStats()
    published_slugs: set[str] = set()

    for page in pages:
        props = page["properties"]
        slug = slugify(title_text(props))
        published_slugs.add(slug)
        wrote, _ = _process_page(
            page,
            section,
            client,
            cache,
            download_assets=download_assets,
        )
        if wrote:
            stats.written += 1
        else:
            stats.skipped += 1

    # Limpeza: remove .md que nao existem mais no Notion (ou foram despublicados).
    for path in section.section_dir.glob("*.md"):
        if path.name == "_index.md":
            continue
        if path.stem not in published_slugs:
            path.unlink()
            stats.removed += 1
            log.info("  removed %s/%s", section.name, path.name)

    cache.save()
    log.info(
        "  %s: %d written, %d up-to-date, %d removed",
        section.name,
        stats.written,
        stats.skipped,
        stats.removed,
    )
    return stats


# --- sync de uma pagina so (debug/dev) ---------------------------------------

def find_page_by_id(client: NotionClient, section: SectionConfig, page_id: str) -> dict:
    """Localiza uma pagina pelo id direto (nao precisa estar no data source)."""

    page = client.get_page(page_id)
    # O GET /pages/{id} nao filtra por Publicar; confiamos no caller.
    return page


def find_page_by_slug(
    client: NotionClient, section: SectionConfig, slug: str
) -> Optional[dict]:
    """Procura uma pagina publicavel cujo slug gerado bate com o fornecido."""

    data_source_id = client.get_data_source_id(section.database_id)
    for page in client.all_pages(data_source_id):
        if slugify(title_text(page["properties"])) == slug:
            return page
    return None


def sync_single_page(
    section: SectionConfig,
    client: NotionClient,
    *,
    slug: Optional[str] = None,
    page_id: Optional[str] = None,
    download_assets: bool = True,
) -> SyncStats:
    """Sincroniza apenas uma pagina. Usado para iteracao rapida/debug.

    - Se `page_id` for fornecido, busca direto pelo id (nao filtra por Publicar).
    - Se `slug` for fornecido, percorre o data source ate achar slug correspondente.
    """

    cache = AssetCache(CACHE_FILE)
    if page_id:
        page = find_page_by_id(client, section, page_id)
    elif slug:
        page = find_page_by_slug(client, section, slug)
        if page is None:
            raise SystemExit(
                f"Nenhuma pagina publicavel com slug={slug!r} em {section.name}"
            )
    else:
        raise SystemExit("sync_single_page exige slug ou page_id")

    wrote, _ = _process_page(
        page, section, client, cache, download_assets=download_assets
    )
    cache.save()
    stats = SyncStats(written=1 if wrote else 0, skipped=0 if wrote else 1)
    return stats