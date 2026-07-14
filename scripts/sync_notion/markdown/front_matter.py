"""Geracao de front matter TOML para Zola.

Usamos `tomli_w` para serializar o dict de forma confiavel e escapar
corretamente strings/listas. O resultado fica entre `+++` ... `+++`,
formato que o Zola entende.
"""

from __future__ import annotations

import tomli_w


def dumps_front_matter(obj: dict) -> str:
    """Serializa um dict para front matter TOML entre `+++`."""

    body = tomli_w.dumps(obj)
    return f"+++\n{body.strip()}\n+++\n"