"""Configuracao do sync: env vars e mapeamento de secoes.

Toda a configuracao vem do ambiente (ver .env / export). As secoes Zola
sincronizadas ficam registradas aqui; para adicionar uma nova secao basta
adicionar uma entrada em `build_sections()`.
"""

from __future__ import annotations

from .env import get_env, notion_token
from .models import SectionConfig
from .paths import CONTENT_ROOT
from .sections.events import build_event_front_matter
from .sections.projects import build_project_front_matter

__all__ = ["get_env", "notion_token", "build_sections"]


def build_sections() -> list[SectionConfig]:
    """Constroi a lista de secoes a sincronizar a partir das env vars.

    Cada secao requer uma env var propria com o id do database Notion.
    """

    projects = SectionConfig(
        database_id=get_env("NOTION_PROJECTS_DB_ID"),
        section_dir=CONTENT_ROOT / "projects",
        name="projects",
        build_front_matter=build_project_front_matter,
    )
    events = SectionConfig(
        database_id=get_env("NOTION_EVENTS_DB_ID"),
        section_dir=CONTENT_ROOT / "events",
        name="events",
        build_front_matter=build_event_front_matter,
    )
    return [projects, events]