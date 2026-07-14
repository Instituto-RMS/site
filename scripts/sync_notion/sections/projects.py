"""Builder de front matter para a secao Projects.

Converte as propriedades da Notion em um dict que o `tomli_w` serializa para
TOML, e monta o conteudo final (front matter + corpo) no formato esperado
pelo template `templates/project.html`.
"""

from __future__ import annotations

from ..markdown.transforms import (
    checkbox_value,
    date_value,
    multi_select_names,
    rich_text,
    select_name,
    title_text,
    url_value,
)
from ..markdown.front_matter import dumps_front_matter
from ..models import Page


def build_project_front_matter(page: dict, slug: str, body: str) -> str:
    """Monta o conteudo final do .md de um projeto."""

    props = page["properties"]
    start_date = date_value(props.get("Início", {}))

    extra: dict = {
        "status": select_name(props.get("Status", {})),
        "tags": multi_select_names(props.get("Tags", {})),
        "partners": rich_text(props.get("Parceiros", {})),
        "highlight": checkbox_value(props.get("Destacado", {})),
        "external_link": url_value(props.get("Link externo", {})),
        "start_date": start_date or "",
    }

    fm: dict = {
        "title": title_text(props),
        "description": rich_text(props.get("Destaque", {})),
        "weight": 10,
        "draft": False,
        "extra": extra,
    }
    # So adiciona `date` no nivel raiz se houver data real; caso contrario
    # o Zola preenche com a data de build por default, o que nao queremos
    # para projetos sem data de inicio.
    if start_date is not None:
        fm["date"] = start_date

    return dumps_front_matter(fm) + "\n\n" + body