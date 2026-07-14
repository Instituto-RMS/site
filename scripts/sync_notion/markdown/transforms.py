"""Transformacoes de dados da Notion: extracao de propriedades, slugify,
limpeza do cabecalho do markdown.

Funcoes puras e faceis de testar. Recebem dicts/strings e devolvem dados
normalizados, sem I/O.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse


# --- propriedades -------------------------------------------------------------

def plain_text(value: dict | list | None) -> str:
    """Extrai texto plano de rich_text/lista da Notion (tolerante ao formato)."""

    if not value:
        return ""
    if isinstance(value, list):
        return "".join(
            part.get("plain_text", part.get("text", {}).get("content", ""))
            for part in value
        )
    if isinstance(value, dict):
        return value.get("plain_text", value.get("text", {}).get("content", ""))
    return str(value)


def rich_text(prop: dict) -> str:
    return plain_text(prop.get("rich_text", [])).strip()


def multi_select_names(prop: dict) -> list[str]:
    return [opt["name"] for opt in prop.get("multi_select", [])]


def select_name(prop: dict) -> str:
    sel = prop.get("select")
    return sel["name"] if sel else ""


def url_value(prop: dict) -> str:
    return prop.get("url") or ""


def date_value(prop: dict) -> str | None:
    d = prop.get("date")
    if not d:
        return None
    return d.get("start") or None


def checkbox_value(prop: dict) -> bool:
    return bool(prop.get("checkbox", False))


def title_text(props: dict) -> str:
    """Extrai o titulo de uma pagina. Procura por 'Nome' (usado nos databases
    do RMS); se nao achar, cai para o primeiro title que existir."""

    nome = props.get("Nome", {})
    if nome.get("title"):
        return plain_text(nome.get("title", [])).strip()
    # fallback generico: primeira propriedade do tipo title.
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return plain_text(prop.get("title", [])).strip()
    return ""


# --- strings ------------------------------------------------------------------

def slugify(text: str) -> str:
    """Normaliza um titulo em slug ASCII seguro."""

    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def parse_notion_time(value: str) -> datetime:
    """Converte timestamp ISO 8601 da Notion em datetime UTC aware."""

    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


# --- limpeza do markdown ------------------------------------------------------

# Chaves de metadados que a Notion escreve no topo do markdown exportado,
# em negrito (ex: **Status:** ...). Quando o front matter ja carrega essas
# informacoes, removemos para evitar duplicacao na pagina.
DEFAULT_METADATA_KEYS = (
    "Status:",
    "Data:",
    "Início:",
    "Tags:",
    "Parceiros:",
    "Destaque:",
    "Local:",
    "Público:",
    "Link externo:",
)


def strip_metadata_markdown(
    markdown: str, keys: tuple[str, ...] = DEFAULT_METADATA_KEYS
) -> str:
    """Remove linhas de metadados em negrito do topo do markdown.

    O parser da Notion escreve essas linhas como `**Status:** Concluido` etc.
    Mantemos o corte generico: removemos qualquer linha que comece com
    `**<chave>` e fique no topo do corpo, ate bater com conteudo real.
    """

    lines = markdown.splitlines()
    while lines and any(lines[0].strip().startswith(f"**{key}") for key in keys):
        lines.pop(0)
    return "\n".join(lines).strip()


# --- nomes de arquivo de midia ------------------------------------------------

def _sanitize_filename(name: str) -> str:
    """Remove caracteres problematicos para sistemas de arquivos."""

    name = re.sub(r"[^\w.\-]", "_", name)
    name = re.sub(r"_+", "_", name).strip("._")
    return name or "image.png"


def _hash_suffix(url: str, length: int = 8) -> str:
    """Devolve um hash curto e estavel do URL para desambiguar nomes iguais."""

    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:length]


def image_filename_from_url(url: str) -> str:
    """Deriva um nome de arquivo estavel a partir de uma URL de imagem.

    A URL pre-assinada da Notion aponta para um path como
    `.../secure.notion-static.com/<uuid>/<nome>.png?X-Amz-...`. Usamos o
    nome original (decoded) quando existe e e razoavel; caso contrario
    geramos um nome a partir do ultimo segmento do path.

    Como uma pagina pode ter varias imagens com o mesmo nome original
    (Notion costuma gerar `image.png`), adicionamos um hash curto do URL
    antes da extensao para garantir unicidade no disco.
    """

    parsed = urlparse(url)
    name = Path(unquote(parsed.path)).name
    if not name or "." not in name:
        parts = [p for p in parsed.path.split("/") if p]
        name = (_sanitize_filename(parts[-1]) + ".png") if parts else "image.png"

    base, ext = _split_ext(name)
    suffix = _hash_suffix(url)
    return f"{_sanitize_filename(base)}_{suffix}{ext}"


def _split_ext(name: str) -> tuple[str, str]:
    """Separa nome/extensao, considerando um possivel '.' no nome base."""

    # Pega a ultima extensao; se nao houver extensao, devolve .bin.
    if "." not in name or name.endswith("."):
        return name, ".bin"
    base, ext = name.rsplit(".", 1)
    return base, f".{ext}"