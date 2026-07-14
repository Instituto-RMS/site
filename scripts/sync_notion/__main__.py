"""Ponto de entrada do pacote: `python -m scripts.sync_notion`.

Monta o cliente Notion, resolve quais secoes sincronizar e chama os
orquestradores de sections/base.py. Suporta sync completo ou de uma
pagina so (para debug rapido).
"""

from __future__ import annotations

import sys

from .cli import build_parser, setup_logging
from .config import build_sections
from .models import SyncOptions, SyncStats
from .notion_client import NotionClient
from .sections.base import sync_section, sync_single_page


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.verbose)

    if args.page and args.page_id:
        parser.error("Use --page ou --page-id, nao ambos.")

    sections = build_sections()
    if args.section:
        sections = [s for s in sections if s.name == args.section]
        if not sections:
            print(f"Nenhuma secao chamada {args.section!r}.", file=sys.stderr)
            return 2

    client = NotionClient()
    options = SyncOptions(
        page_slug=args.page,
        page_id=args.page_id,
        download_assets=not args.no_download,
    )

    total = SyncStats()

    # Modo debug: sincroniza so uma pagina, procurando em cada secao.
    if options.page_slug or options.page_id:
        for section in sections:
            try:
                stats = sync_single_page(
                    section,
                    client,
                    slug=options.page_slug,
                    page_id=options.page_id,
                    download_assets=options.download_assets,
                )
                total.merge(stats)
                print(
                    f"  {section.name}: {stats.written} written, "
                    f"{stats.skipped} up-to-date"
                )
                break  # so processamos na primeira secao que encontrar
            except SystemExit as exc:
                # Pagina nao encontrada nesta secao: tenta a proxima.
                if options.page_id:
                    raise
                continue
        else:
            print("Pagina nao encontrada em nenhuma secao.", file=sys.stderr)
            return 1
        print(f"Done. {total.written} written, {total.skipped} up-to-date.")
        return 0

    # Modo completo.
    for section in sections:
        stats = sync_section(
            section, client, download_assets=options.download_assets
        )
        total.merge(stats)

    print(
        f"Done. {total.written} written, {total.skipped} up-to-date, "
        f"{total.removed} removed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())