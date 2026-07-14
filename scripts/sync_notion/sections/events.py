"""Builder de front matter para a secao Events.

Converte as propriedades da Notion em front matter TOML e devolve o
conteudo final (front matter + corpo) para o template `templates/event.html`.
"""

from __future__ import annotations

from ..markdown.front_matter import dumps_front_matter
from ..markdown.transforms import (
    checkbox_value,
    date_value,
    multi_select_names,
    rich_text,
    select_name,
    title_text,
    url_value,
)


def build_event_front_matter(page: dict, slug: str, body: str) -> str:
    """Monta o conteudo final do .md de um evento."""

    props = page["properties"]
    event_date = date_value(props.get("Data", {}))

    extra: dict = {
        "status": select_name(props.get("Status", {})),
        "tags": multi_select_names(props.get("Tags", {})),
        "location": rich_text(props.get("Local", {})),
        "audience": rich_text(props.get("Público", {})),
        "partners": rich_text(props.get("Parceiros", {})),
        "highlight": checkbox_value(props.get("Destacado", {})),
        "external_link": url_value(props.get("Link externo", {})),
    }
    if event_date is None:
        extra["date_text"] = "Data a marcar"

    description = (
        rich_text(props.get("Destaque", {}))
        or select_name(props.get("Status", {}))
    )
    fm: dict = {
        "title": title_text(props),
        "description": description,
        "draft": False,
        "extra": extra,
        # Usa a data real quando existir; senao pin em 2099 para TBA aparecer
        # no final da listagem (ordenada por data).
        "date": event_date if event_date is not None else "2099-12-31",
    }

    return dumps_front_matter(fm) + "\n\n" + body