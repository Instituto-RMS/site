"""CLI do sync Notion -> Zola.

Args:
    --page <slug>           Sincroniza apenas a pagina com o slug informado,
                            em qualquer secao que ela exista.
    --page-id <notion-id>   Sincroniza uma pagina diretamente pelo id do Notion.
    --section <name>         Restringe o sync a uma secao (projects|events).
    --no-download            Nao baixa imagens (reescreve URLs sem salvar).
"""

from __future__ import annotations

import argparse
import logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.sync_notion",
        description="Sincroniza databases do Notion para arquivos de conteudo Zola.",
    )
    parser.add_argument(
        "--page",
        help="Sincroniza apenas a pagina com este slug (fluxo de debug).",
    )
    parser.add_argument(
        "--page-id",
        help="Sincroniza uma pagina diretamente pelo id do Notion.",
    )
    parser.add_argument(
        "--section",
        choices=["projects", "events"],
        help="Restringe o sync a uma secao especifica.",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Nao baixa imagens (apenas reescreve URLs, util em testes secos).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Nivel de log (-v info, -vv debug).",
    )
    return parser


def setup_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )