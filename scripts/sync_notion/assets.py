"""Download de assets (imagens) da Notion para static/notion/images/.

As URLs que a Notion devolve sao pre-assinadas e expiram em ~1h. Para um
site estatico, precisamos baixar as imagens durante o sync e referenciar
um caminho local estavel no markdown gerado.

Fluxo:
    1. Recebe a URL pre-assinada.
    2. Verifica o cache por URL. Se ja baixamos essa URL (e o arquivo
       ainda existe em disco), reaproveita.
    3. Caso contrario, baixa o arquivo, calcula o sha256 e registra no cache.

A organizacao em disco e:
    static/notion/images/{section}/{slug}/{arquivo}
A URL publica usada no markdown e:
    /notion/images/{section}/{slug}/{arquivo}
"""

from __future__ import annotations

import logging
from pathlib import Path

import requests

from .cache import AssetCache, file_sha256
from .markdown.transforms import image_filename_from_url
from .models import DownloadedAsset

log = logging.getLogger(__name__)


class AssetDownloader:
    """Baixa e cacheia imagens da Notion.

    O downloader e contextualizado por secao e slug: ele sabe onde salvar
    os arquivos e qual path web usar. O cache e compartilhado entre todas
    as instancias (arquivo unico em static/notion/.cache.json).
    """

    def __init__(
        self,
        *,
        images_root: Path,
        web_prefix: str,
        section: str,
        slug: str,
        cache: AssetCache,
        session: requests.Session | None = None,
        download: bool = True,
    ) -> None:
        self._images_root = images_root
        self._web_prefix = web_prefix
        self._section = section
        self._slug = slug
        self._cache = cache
        self._session = session or requests.Session()
        self._download = download

    @property
    def section_dir(self) -> Path:
        return self._images_root / self._section / self._slug

    @property
    def section_web_prefix(self) -> str:
        return f"{self._web_prefix}/{self._section}/{self._slug}"

    def download(self, url: str) -> DownloadedAsset:
        """Baixa (ou reaproveita do cache) uma imagem e devolve o asset.

        Levanta excecao em caso de falha de rede; o caller (renderer) decide
        se loga e segue ou aborta.
        """

        cached = self._cache.get(url)
        if cached and Path(cached["local_path"]).exists():
            return DownloadedAsset(
                source_url=url,
                local_path=Path(cached["local_path"]),
                web_path=cached["web_path"],
            )

        filename = image_filename_from_url(url)
        local_path = self.section_dir / filename
        web_path = f"{self.section_web_prefix}/{filename}"

        if self._download:
            self._section_dir_mkdir()
            self._fetch(url, local_path)
            sha = file_sha256(local_path)
            size = local_path.stat().st_size
            self._cache.put(
                url,
                local_path=local_path,
                web_path=web_path,
                content_sha256=sha,
                size=size,
            )
            log.info("asset baixado: %s -> %s", url, web_path)
        else:
            # Modo sem download (testes): nao toca no disco, so devolve o path.
            pass

        return DownloadedAsset(
            source_url=url, local_path=local_path, web_path=web_path
        )

    def _section_dir_mkdir(self) -> None:
        self.section_dir.mkdir(parents=True, exist_ok=True)

    def _fetch(self, url: str, dest: Path) -> None:
        resp = self._session.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)