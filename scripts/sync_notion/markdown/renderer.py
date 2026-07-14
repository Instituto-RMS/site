"""Renderer de markdown: reescrita de URLs de midia e conversao de `<columns>`.

A API da Notion devolve o conteudo da pagina em "enhanced markdown", que mistura
Markdown puro com tags HTML (callouts, colunas, tabelas, etc.). Para um site
Zola precisamos:

1. Baixar imagens (URLs pre-assinadas expiram em ~1h) e reescrever os `src`
   para caminhos locais estaveis em /notion/images/...
2. Converter blocos `<columns>...<column>...</column></columns>` em shortcodes
   Zola `{{ columns() }}...{{ column() }}...{{ end }}...{{ end }}`, que sao
   renderizados pelo template `templates/shortcodes/columns.html`.

A funcao principal `render_markdown()` coordena essas transformacoes. A
estrategia e puramente baseada em regex sobre o texto (nao fazemos parse HTML
completo): a Notion produz um formato estavel, entao regex e suficiente e
mantem o codigo curto e testavel.
"""

from __future__ import annotations

import logging
import re
from html import escape
from typing import Optional

from ..assets import AssetDownloader
from .transforms import image_filename_from_url, strip_metadata_markdown

log = logging.getLogger(__name__)

# Regex para imagens no formato Markdown: ![alt](url)
# Captura caption (alt) e a URL. URLs podem conter parenteses quando
# codificadas; usamos [^)] para manter simples (as URLs pre-assinadas da Notion
# nao contem ')' crus).
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

# Regex para <columns>...</columns> (com possivel whitespace/quebras entre).
_COLUMNS_OPEN_RE = re.compile(r"<columns\s*>", re.IGNORECASE)
_COLUMNS_CLOSE_RE = re.compile(r"</columns\s*>", re.IGNORECASE)
_COLUMN_OPEN_RE = re.compile(r"<column\s*>", re.IGNORECASE)
_COLUMN_CLOSE_RE = re.compile(r"</column\s*>", re.IGNORECASE)

# Outras tags HTML fantasmas que a Notion insere e que nao renderizam.
# Removemos da saida.
_EMPTY_BLOCK_RE = re.compile(r"<empty-block\s*/?>", re.IGNORECASE)
_DIVIDER_RE = re.compile(r"<hr\s*/?>", re.IGNORECASE)


def render_markdown(
    markdown: str,
    *,
    asset_downloader: Optional[AssetDownloader] = None,
    strip_metadata: bool = True,
) -> str:
    """Aplica todas as transformacoes no markdown da Notion.

    - `asset_downloader`: se fornecido, baixa imagens e reescreve URLs. Se None,
      nao toca nas URLs (usado em testes e no modo sem download).
    - `strip_metadata`: se True, remove as linhas de metadados em negrito do topo
      (Status, Data, etc.) que o front matter ja cobre.
    """

    text = markdown
    if strip_metadata:
        text = strip_metadata_markdown(text)

    text = _rewrite_images(text, asset_downloader)
    text = _convert_columns(text)
    text = _clean_ghost_tags(text)

    return text.strip() + "\n"


# --- imagens ------------------------------------------------------------------

def _rewrite_images(text: str, downloader: Optional[AssetDownloader]) -> str:
    """Encontra `![caption](url)`, baixa a imagem e reescreve para caminho local."""

    if downloader is None:
        return text

    def _replace(match: re.Match) -> str:
        caption, url = match.group(1), match.group(2)
        try:
            asset = downloader.download(url)
        except Exception as exc:  # noqa: BLE001 - queremos continuar o sync
            log.warning("Falha baixando %s: %s", url, exc)
            return match.group(0)
        return f'<img src="{asset.web_path}" alt="{escape(caption)}">'

    return _IMAGE_RE.sub(_replace, text)


# --- colunas ------------------------------------------------------------------

def _convert_columns(text: str) -> str:
    """Converte `<columns>`/`<column>` da Notion em shortcodes Zola.

    A Notion gera:

        <columns>
            <column>
                ...conteudo...
            </column>
            <column>
                ...
            </column>
        </columns>

    Convertemos para:

        {{ columns() }}
        {{ column() }}
        ...conteudo...
        {{ end }}
        {{ column() }}
        ...
        {{ end }}
        {{ end }}

    Funciona para qualquer conteudo dentro de colunas, nao so imagens.
    """

    text = _COLUMNS_OPEN_RE.sub("{% columns() %}", text)
    text = _COLUMNS_CLOSE_RE.sub("{% end %}", text)
    text = _COLUMN_OPEN_RE.sub("{% column() %}", text)
    text = _COLUMN_CLOSE_RE.sub("{% end %}", text)
    return text


def _clean_ghost_tags(text: str) -> str:
    """Remove tags HTML fantasmas da Notion (`<empty-block/>`, `<hr/>`)."""

    text = _EMPTY_BLOCK_RE.sub("", text)
    text = _DIVIDER_RE.sub("---", text)
    return text