# ruff: noqa: S101
import asyncio
import json
from pathlib import Path
from typing import Any

import httpx

from ews_api._api import EwsApi, MetaData, PriceData

EXAMPLE_PATH = Path(__file__).parent / "examples" / "example.json"
EXAMPLE_DATA: dict[str, Any] = json.loads(EXAMPLE_PATH.read_text())


def test_price_data_from_json():
    item = EXAMPLE_DATA["today"][0]
    price = PriceData.from_json(item)
    assert price.dynamic_price == item["dynamic"]
    assert price.static_price == item["fix"]
    assert price.total_price == item["total"]
    assert price.starts_at.isoformat() == "2025-12-08T00:00:00+01:00"


def test_fetch_populates_meta_and_prices(monkeypatch):
    api = EwsApi("dummy-token")

    async def fake_get(self, url):  # noqa: RUF029
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json=EXAMPLE_DATA)

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    success = asyncio.run(api.fetch())

    assert success is True
    assert api.meta == MetaData(
        interval=EXAMPLE_DATA["interval"],
        interval_unit=EXAMPLE_DATA["intervalUnit"],
        unit=EXAMPLE_DATA["priceUnit"],
        tariff=EXAMPLE_DATA["tariff"],
    )
    combined = EXAMPLE_DATA["today"] + EXAMPLE_DATA["tomorrow"]
    assert len(api.data) == len(combined)
    first = api.data[0]
    assert first.dynamic_price == combined[0]["dynamic"]
    assert first.total_price == combined[0]["total"]


def test_fetch_handles_http_error(monkeypatch):
    api = EwsApi("dummy-token")

    async def fake_get(self, url):  # noqa: RUF029
        request = httpx.Request("GET", url)
        return httpx.Response(500, request=request, json={})

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    success = asyncio.run(api.fetch())

    assert success is False
    assert api.meta is None
    assert api.data == []


def test_get_wraps_fetch(monkeypatch):
    api = EwsApi("dummy-token")

    async def fake_get(self, url):  # noqa: RUF029
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json=EXAMPLE_DATA)

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    data = asyncio.run(api.get())

    assert isinstance(data, list)
    assert len(data) == len(EXAMPLE_DATA["today"] + EXAMPLE_DATA["tomorrow"])


def test_authenticate_success(monkeypatch):
    def fake_get(url, headers=None):  # type: ignore[override]
        request = httpx.Request("GET", url, headers=headers or {})
        return httpx.Response(200, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)

    result = asyncio.run(EwsApi.authenticate("valid-key"))
    assert result is True


def test_authenticate_handles_http_exception(monkeypatch):
    def fake_get(url, headers=None):  # type: ignore[override]
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx, "get", fake_get)

    result = asyncio.run(EwsApi.authenticate("invalid-key"))
    assert result is False
