"""Cliente HTTP da Notion: headers, retry, rate-limit e paginação.

Encapsula todo o acesso à API para que o resto do codigo nao precise saber
de URLs, headers ou backoff. As funcoes de transformacao recebem dados ja
consultados (ou um cliente injetado em casos de paginacao/children).
"""

from __future__ import annotations

import time
from typing import Any, Iterator, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .env import notion_token
from .paths import NOTION_API, NOTION_VERSION


class NotionError(Exception):
    """Erro de comunicacao com a Notion (apos retries esgotados)."""


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {notion_token()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


class NotionClient:
    """Cliente fino com retry exponencial e respeito ao Retry-After.

    Mantem state minimo (session) para reusar conexoes. A ideia e que o
    resto do codigo injete este objeto onde precisar paginacao ou fetch
    de children (tabelas, colunas, etc.), sem acoplar a biblioteca HTTP.
    """

    def __init__(self, api: str = NOTION_API) -> None:
        self._api = api
        self._session = requests.Session()

    @retry(
        retry=retry_if_exception_type((requests.RequestException, NotionError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict[str, Any]:
        url = f"{self._api}{path}"
        resp = self._session.request(
            method, url, headers=_headers(), params=params, json=json, timeout=60
        )

        # Rate limit: respeita o Retry-After (em segundos) antes de re-tentar.
        if resp.status_code in (429, 529):
            retry_after = int(resp.headers.get("Retry-After", "5"))
            time.sleep(retry_after)
            raise NotionError(f"rate limited (status {resp.status_code})")

        if 500 <= resp.status_code < 600:
            raise NotionError(f"notion {resp.status_code}: {resp.text[:200]}")

        resp.raise_for_status()
        return resp.json()

    # --- endpoints de alto nivel -------------------------------------------------

    def get_data_source_id(self, database_id: str) -> str:
        """Resolve o primeiro data source id de um database."""

        db = self.request("GET", f"/databases/{database_id}")
        sources = db.get("data_sources", [])
        if not sources:
            raise NotionError(f"Database {database_id} has no data_sources")
        return sources[0]["id"]

    def query_data_source(
        self,
        data_source_id: str,
        *,
        start_cursor: Optional[str] = None,
        page_size: int = 100,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filter": {"property": "Publicar", "checkbox": {"equals": True}},
            "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
            "page_size": page_size,
        }
        if start_cursor:
            body["start_cursor"] = start_cursor
        return self.request(
            "POST", f"/data_sources/{data_source_id}/query", json=body
        )

    def all_pages(self, data_source_id: str) -> list[dict[str, Any]]:
        """Itera todas as paginas publicaveis de um data source."""

        pages: list[dict[str, Any]] = []
        cursor: Optional[str] = None
        while True:
            data = self.query_data_source(data_source_id, start_cursor=cursor)
            pages.extend(data.get("results", []))
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                break
        return pages

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{page_id}")

    def fetch_markdown(self, page_id: str) -> str:
        data = self.request("GET", f"/pages/{page_id}/markdown")
        return data.get("markdown", "")

    def block_children(self, block_id: str) -> Iterator[dict[str, Any]]:
        """Itera os filhos de um bloco (paginado).

        Necessario para colunas e tabelas: a API de markdown exporta a
        estrutura, mas para baixar imagens dentro de colunas precisamos
        percorrer os filhos. Por enquanto mantemos como utilidade.
        """

        cursor: Optional[str] = None
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            data = self.request(
                "GET", f"/blocks/{block_id}/children", params=params
            )
            for block in data.get("results", []):
                yield block
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                break