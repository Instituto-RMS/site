"""Cache local de assets baixados da Notion.

As URLs de imagens da Notion sao pre-assinadas e expiram em ~1h. A cada
execucao do sync, a URL muda mas o conteudo (arquivo) costuma ser o mesmo.
Para nao baixar a mesma imagem toda vez, mantemos um cache em disco:

    static/notion/.cache.json
        {
            "<url_hash>": {
                "url": "<url original>",
                "local_path": "static/notion/images/projects/foo/img.png",
                "web_path": "/notion/images/projects/foo/img.png",
                "content_sha256": "<hash do arquivo>",
                "size": 12345
            }
        }

A chave e um hash da URL original (que muda a cada fetch), mas guardamos
tambem o content_sha256 para detectar se o arquivo mudou. Em practice,
dedup por caminho local (se o arquivo ja existe e tem mesmo conteudo,
reaproveitamos).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional


class AssetCache:
    """Cache JSON simples em disco para assets baixados."""

    def __init__(self, cache_file: Path) -> None:
        self._file = cache_file
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self._file.exists():
            try:
                self._data = json.loads(self._file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def save(self) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def url_hash(url: str) -> str:
        return hashlib.blake2b(url.encode(), digest_size=12).hexdigest()

    def get(self, url: str) -> Optional[dict]:
        return self._data.get(self.url_hash(url))

    def put(
        self,
        url: str,
        *,
        local_path: Path,
        web_path: str,
        content_sha256: str,
        size: int,
    ) -> None:
        self._data[self.url_hash(url)] = {
            "url": url,
            "local_path": str(local_path),
            "web_path": web_path,
            "content_sha256": content_sha256,
            "size": size,
        }


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()