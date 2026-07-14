"""Testes das transformacoes de dados da Notion (transforms.py)."""

from scripts.sync_notion.markdown.transforms import (
    checkbox_value,
    date_value,
    multi_select_names,
    plain_text,
    rich_text,
    select_name,
    slugify,
    strip_metadata_markdown,
    title_text,
    url_value,
)


# --- propriedades -------------------------------------------------------------

def test_plain_text_list():
    parts = [
        {"plain_text": "Hello "},
        {"plain_text": "world"},
    ]
    assert plain_text(parts) == "Hello world"


def test_plain_text_dict_fallback():
    # Sem plain_text, cai em text.content
    assert plain_text({"text": {"content": "abc"}}) == "abc"


def test_plain_text_none():
    assert plain_text(None) == ""


def test_rich_text_strips():
    prop = {"rich_text": [{"plain_text": "  Rio Maker Space  "}]}
    assert rich_text(prop) == "Rio Maker Space"


def test_multi_select_names():
    prop = {"multi_select": [{"name": "foguete"}, {"name": "balao"}]}
    assert multi_select_names(prop) == ["foguete", "balao"]


def test_select_name():
    assert select_name({"select": {"name": "Concluido"}}) == "Concluido"
    assert select_name({"select": None}) == ""


def test_url_value():
    assert url_value({"url": "https://exemplo.com"}) == "https://exemplo.com"
    assert url_value({"url": None}) == ""


def test_date_value():
    assert date_value({"date": {"start": "2025-01-01"}}) == "2025-01-01"
    assert date_value({"date": None}) is None


def test_checkbox_value():
    assert checkbox_value({"checkbox": True}) is True
    assert checkbox_value({"checkbox": False}) is False
    assert checkbox_value({}) is False


def test_title_text_uses_nome():
    props = {"Nome": {"title": [{"plain_text": "StarChain"}]}}
    assert title_text(props) == "StarChain"


def test_title_text_fallback_generic_title():
    # Quando nao ha "Nome", cai na primeira propriedade do tipo title.
    props = {
        "Outro": {"type": "title", "title": [{"plain_text": "Foo"}]},
    }
    assert title_text(props) == "Foo"


# --- slugify ------------------------------------------------------------------

def test_slugify_ascii():
    assert slugify("StarChain — Infraestrutura Orbital") == "starchain-infraestrutura-orbital"


def test_slugify_accents_and_symbols():
    assert slugify("Café & Bolo") == "cafe-bolo"


def test_slugify_empty():
    # So removemos simbolos nao-word; hifens soltos sobrevivem como hifen.
    assert slugify("---") == "-"


def test_slugify_no_meaningful_content():
    assert slugify("") == ""
    assert slugify("   ") == ""


# --- strip_metadata_markdown --------------------------------------------------

def test_strip_metadata_removes_known_keys():
    md = "**Status:** Concluido\n**Data:** 2025-01-01\n\nConteudo real."
    out = strip_metadata_markdown(md)
    assert out.startswith("Conteudo real.")
    assert "Status" not in out


def test_strip_metadata_preserves_body_without_metadata():
    md = "Conteudo sem metadados."
    assert strip_metadata_markdown(md) == "Conteudo sem metadados."