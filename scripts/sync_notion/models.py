"""Modelos de dados do sync.

Usamos dataclasses para representar as entidades que circulam entre as
camadas (cliente Notion -> processamento -> escrita de arquivos). Mantemos
os modelos minuciosos e imutaveis onde faz sentido, para facilitar testes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class SectionConfig:
    """Configuracao de uma secao Zola sincronizada a partir de um database Notion.

    - `database_id`: id do database Notion de origem.
    - `section_dir`: diretorio alvo em content/, ex: content/projects.
    - `name`: nome curto usado em logs e no caminho das imagens, ex: "projects".
    - `build_front_matter`: funcao que recebe (page, slug, markdown) e devolve
      o conteudo completo do arquivo .md (front matter + corpo).
    """

    database_id: str
    section_dir: Path
    name: str
    build_front_matter: "FrontMatterBuilder"


@dataclass(frozen=True)
class DownloadedAsset:
    """Representa um arquivo de midia baixado da Notion.

    - `source_url`: URL original (pre-assinada e expira em ~1h) retornada pela API.
    - `local_path`: caminho absoluto do arquivo baixado em static/notion/images/...
    - `web_path`: caminho publico a ser usado no markdown, ex: /notion/images/.../x.png.
    """

    source_url: str
    local_path: Path
    web_path: str


@dataclass
class Page:
    """Uma pagina Notion ja consultada, com suas propriedades brutas.

    Mantemos o dict original para que os builders possam extrair campos
    especificos (Nome, Status, Tags, etc.) sem que o modelo precise conhecer
    todas as variantes de schema.
    """

    id: str
    last_edited_time: str
    properties: dict
    raw: dict = field(repr=False)

    @property
    def title(self) -> str:
        from .markdown.transforms import title_text

        return title_text(self.properties)

    @property
    def slug(self) -> str:
        from .markdown.transforms import slugify

        return slugify(self.title)


# Tipo funcional dos builders de front matter.
FrontMatterBuilder = Callable[["Page", str, str], str]


@dataclass
class SyncStats:
    """Estatisticas de uma execucao de sync de secao."""

    written: int = 0
    skipped: int = 0
    removed: int = 0
    downloaded_assets: int = 0

    def merge(self, other: "SyncStats") -> None:
        self.written += other.written
        self.skipped += other.skipped
        self.removed += other.removed
        self.downloaded_assets += other.downloaded_assets


@dataclass
class SyncOptions:
    """Opcoes de execucao do sync.

    - `page_slug`: quando definido, sincroniza apenas a pagina com o slug
      informado (fluxo de debug). Caso contrario, sincroniza tudo.
    - `page_id`: alternativa ao slug, identificando a pagina diretamente no
      Notion pelo id (util quando a pagina ainda nao foi gerada localmente).
    - `download_assets`: se False, apenas reescreve URLs sem baixar midia.
      util em testes ou em ambientes sem rede.
    """

    page_slug: Optional[str] = None
    page_id: Optional[str] = None
    download_assets: bool = True