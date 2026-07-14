"""Testes do gerador de front matter TOML."""

from scripts.sync_notion.markdown.front_matter import dumps_front_matter


def test_dumps_front_matter_simple():
    out = dumps_front_matter({"title": "Foo", "weight": 10})
    assert out.startswith("+++\n")
    assert out.rstrip().endswith("+++")
    assert 'title = "Foo"' in out
    assert "weight = 10" in out


def test_dumps_front_matter_nested_extra():
    out = dumps_front_matter(
        {
            "title": "StarChain",
            "extra": {"tags": ["sat", "leo"], "highlight": True},
        }
    )
    assert "[extra]" in out
    # tomli_w formata listas em multiplas linhas; checamos os elementos.
    assert '"sat"' in out
    assert '"leo"' in out
    assert "highlight = true" in out


def test_dumps_front_matter_handles_unicode():
    out = dumps_front_matter({"title": "Café com Açúcar"})
    assert "Café com Açúcar" in out