"""Leitura de variaveis de ambiente.

Modulo isolado para evitar ciclos: `notion_client` precisa do token, mas
`config` importa `sections` (que importa `notion_client`). Mantemos a
leitura de env aqui, sem depender de nada do pacote.
"""

from __future__ import annotations

import os


def get_env(name: str) -> str:
    """Le uma variavel de ambiente obrigatoria. Falha com mensagem clara."""

    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing environment variable: {name}")
    return value


def notion_token() -> str:
    return get_env("NOTION_TOKEN")