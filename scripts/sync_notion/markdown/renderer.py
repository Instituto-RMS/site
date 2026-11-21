"""Renderer de markdown: reescrita de URLs de midia e conversao de `<columns>`.

A API da Notion devolve o conteudo da pagina em "enhanced markdown", que mistura
Markdown puro com tags HTML (callouts, colunas, tabelas, etc.). Para um site
Zola precisamos:

1. Baixar imagens (URLs pre-assinadas expiram em ~1h) e reescrever os `src`
   para caminhos locais estaveis em /notion/images/...
2. Converter blocos `<columns>...<column>...</column></columns>` em componentes
   Tera `{% <columns> %}...{% <column> %}...{% </column> %}...{% </columns> %}`,
   renderizados pelos templates `templates/_components/columns.html` e
   `templates/_components/column.html` (Zola 0.23+ removeu shortcodes).

A funcao principal `render_markdown()` coordena essas transformacoes. A
estrategia e puramente baseada em regex sobre o texto (nao fazemos parse HTML
completo): a Notion produz um formato estavel, entao regex e suficiente e
mantem o codigo curto e testavel.
"""

from __future__ import annotations

import logging
import re
import textwrap
from html import escape
from typing import Optional
from urllib.parse import unquote, urlparse

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
# <column> pode vir com atributo `ratio="33.33"` (Notion). Capturamos o valor
# para repassar ao componente Zola `{% <column ratio={...}> %}`.
_COLUMN_OPEN_RE = re.compile(r'<column(?:\s+ratio="([0-9.]+)")?\s*>', re.IGNORECASE)
_COLUMN_CLOSE_RE = re.compile(r"</column\s*>", re.IGNORECASE)

# Ja no formato de componente: usado para dedentar corpos. O Tera remove as
# linhas das tags, mas preserva a indentacao do corpo; como o Markdown trata
# 4+ espacos (ou um tab) como bloco de codigo, um corpo indentado viraria
# `<pre>` em vez de HTML/Markdown normal.
_COMPONENT_COLUMNS_RE = re.compile(
    r"\{% <columns> %\}(.*?)\{% </columns> %\}", re.DOTALL
)
_COMPONENT_COLUMN_RE = re.compile(
    r"\{% <column(?: ratio=\{[0-9.]+\})?> %\}(.*?)\{% </column> %\}", re.DOTALL
)

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
        # A Notion as vezes devolve "URLs" que na verdade sao blobs
        # codificados em JSON do tipo `file://{"source":"attachment:...":...}`
        # (vindos de anexos que nao foram exportados como arquivo real).
        # `requests` nao tem adapter para `file://` e essas URLs nao sao
        # buscaveis; pulamos em vez de tentar baixar.
        if not _is_fetchable(url):
            log.warning(
                "pulando imagem com URL nao-buscavel (scheme=%r): %s",
                urlparse(url).scheme,
                url,
            )
            return match.group(0)
        try:
            asset = downloader.download(url)
        except Exception as exc:  # noqa: BLE001 - queremos continuar o sync
            log.warning("Falha baixando %s: %s", url, exc)
            return match.group(0)
        return f'<img src="{asset.web_path}" alt="{escape(caption)}">'

    return _IMAGE_RE.sub(_replace, text)


def _is_fetchable(url: str) -> bool:
    """True se a URL tem scheme http/https (buscavel via requests)."""

    scheme = urlparse(url).scheme.lower()
    return scheme in ("http", "https")


# --- colunas ------------------------------------------------------------------

def _convert_columns(text: str) -> str:
    """Converte `<columns>`/`<column>` da Notion em componentes Tera.

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

        {% <columns> %}
        {% <column> %}
        ...conteudo...
        {% </column> %}
        {% <column> %}
        ...
        {% </column> %}
        {% </columns> %}

    Funciona para qualquer conteudo dentro de colunas, nao so imagens.

    O corpo de cada componente e dedentado: o Tera remove as linhas das tags,
    mas o Markdown trataria a indentacao restante (4+ espacos/tab) como bloco
    de codigo, transformando as imagens em `<pre>`.
    """

    text = _COLUMNS_OPEN_RE.sub("{% <columns> %}", text)
    text = _COLUMNS_CLOSE_RE.sub("{% </columns> %}", text)

    def _column_repl(match: re.Match) -> str:
        ratio = match.group(1)
        if ratio:
            # O componente declara `ratio: float`; literais inteiros precisam de
            # casa decimal para o Tera aceitar o argumento.
            if "." not in ratio:
                ratio += ".0"
            return "{% <column ratio={" + ratio + "}> %}"
        return "{% <column> %}"

    text = _COLUMN_OPEN_RE.sub(_column_repl, text)
    text = _COLUMN_CLOSE_RE.sub("{% </column> %}", text)
    return _dedent_component_bodies(text)


def _dedent_component_bodies(text: str) -> str:
    """Remove a indentacao comum dos corpos de `<columns>`/`<column>`.

    Processa primeiro `<columns>` (mais externo) e depois `<column>`, de modo
    que cada corpo perca um nivel de indentacao, preservando a indentacao
    relativa interna (listas, continuacoes, etc.).
    """

    def _dedent(match: re.Match) -> str:
        whole = match.group(0)
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.start(0)
        return whole[:start] + textwrap.dedent(match.group(1)) + whole[end:]

    text = _COMPONENT_COLUMNS_RE.sub(_dedent, text)
    return _COMPONENT_COLUMN_RE.sub(_dedent, text)


def _clean_ghost_tags(text: str) -> str:
    """Remove tags HTML fantasmas da Notion (`<empty-block/>`, `<hr/>`)."""

    text = _EMPTY_BLOCK_RE.sub("", text)
    text = _DIVIDER_RE.sub("---", text)
    return text