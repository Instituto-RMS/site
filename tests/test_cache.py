"""Testes do cache de assets."""

from pathlib import Path

from scripts.sync_notion.cache import AssetCache, file_sha256


def test_cache_roundtrip(tmp_path: Path):
    cache_file = tmp_path / "cache.json"
    cache = AssetCache(cache_file)
    cache.put(
        "https://exemplo.com/img.png",
        local_path=tmp_path / "img.png",
        web_path="/notion/images/projects/x/img.png",
        content_sha256="abc",
        size=42,
    )
    cache.save()
    assert cache_file.exists()

    cache2 = AssetCache(cache_file)
    entry = cache2.get("https://exemplo.com/img.png")
    assert entry is not None
    assert entry["web_path"] == "/notion/images/projects/x/img.png"
    assert entry["size"] == 42


def test_cache_missing(tmp_path: Path):
    cache = AssetCache(tmp_path / "nope.json")
    assert cache.get("https://x") is None


def test_file_sha256(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_bytes(b"hello")
    # sha256("hello") conhecido
    assert file_sha256(f) == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )