"""Testes do renderer de markdown (imagens e colunas)."""

from scripts.sync_notion.markdown.renderer import (
    _clean_ghost_tags,
    _convert_columns,
    render_markdown,
)
from scripts.sync_notion.markdown.transforms import image_filename_from_url


# --- colunas ------------------------------------------------------------------

def test_convert_columns_basic():
    src = (
        "<columns>\n"
        "<column>\nconteudo A\n</column>\n"
        "<column>\nconteudo B\n</column>\n"
        "</columns>"
    )
    out = _convert_columns(src)
    assert "{% columns() %}" in out
    assert "{% end %}" in out
    assert "{% column() %}" in out
    assert "<columns>" not in out
    assert "</column>" not in out


def test_convert_columns_case_insensitive():
    src = "<COLUMNS><COLUMN>x</COLUMN></COLUMNS>"
    out = _convert_columns(src)
    assert "{% columns() %}" in out
    assert "{% column() %}" in out


def test_convert_columns_preserves_ratio():
    src = (
        '<columns>\n'
        '<column ratio="33.33">A</column>\n'
        '<column ratio="33.33">B</column>\n'
        '<column ratio="33.33">C</column>\n'
        "</columns>"
    )
    out = _convert_columns(src)
    assert '{% column(ratio=33.33) %}' in out
    assert "<column" not in out


def test_convert_columns_mixed_ratio_and_plain():
    src = (
        '<columns>\n'
        '<column ratio="50">A</column>\n'
        '<column>B</column>\n'
        "</columns>"
    )
    out = _convert_columns(src)
    assert '{% column(ratio=50) %}' in out
    assert '{% column() %}' in out
    assert "<column" not in out


# --- imagens (sem download) ---------------------------------------------------

def test_render_markdown_without_downloader_keeps_urls():
    md = "![legenda](https://exemplo.com/img.png)"
    out = render_markdown(md, asset_downloader=None)
    assert "https://exemplo.com/img.png" in out
    assert out.endswith("\n")


def test_render_markdown_strips_metadata_by_default():
    md = "**Status:** Foo\n\n# Titulo\n\nCorpo."
    out = render_markdown(md, asset_downloader=None)
    assert out.startswith("# Titulo")


def test_render_markdown_can_skip_strip():
    md = "**Status:** Foo\n\n# Titulo"
    out = render_markdown(md, asset_downloader=None, strip_metadata=False)
    assert out.startswith("**Status:**")


# --- nome de arquivo de imagem -----------------------------------------------

def test_image_filename_from_url_extracts_name():
    url = (
        "https://s3.amazonaws.com/secure.notion-static.com"
        "/abc-123/foguete.png?X-Amz-Signature=xyz"
    )
    name = image_filename_from_url(url)
    assert name.startswith("foguete_")
    assert name.endswith(".png")


def test_image_filename_from_url_uses_hash_for_same_basename():
    # Duas URLs com mesmo nome base devem gerar nomes distintos.
    url_a = "https://exemplo.com/image.png?sig=aaaa"
    url_b = "https://exemplo.com/image.png?sig=bbbb"
    assert image_filename_from_url(url_a) != image_filename_from_url(url_b)


def test_image_filename_from_url_fallback():
    url = "https://exemplo.com/sem-extensao/"
    name = image_filename_from_url(url)
    assert name.endswith(".png")


def test_clean_ghost_tags_removes_empty_block():
    assert _clean_ghost_tags("<empty-block/>\n# Oi").strip() == "# Oi"


def test_clean_ghost_tags_converts_hr():
    assert _clean_ghost_tags("linha\n<hr/>\noutra").strip() == "linha\n---\noutra"