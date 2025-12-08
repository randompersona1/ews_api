from __future__ import annotations
import datetime
from dataclasses import dataclass

import httpx

from ews_api.const import EWS_DATA_URI
from ews_api.utils import build_user_agent


@dataclass
class MetaData:
    interval: int
    interval_unit: str
    unit: str
    tariff: str


@dataclass
class PriceData:
    dynamic_price: float
    static_price: float
    total_price: float
    starts_at: datetime.datetime

    @classmethod
    def from_json(cls, json: dict) -> PriceData:
        return cls(
            dynamic_price=json["dynamic"],
            static_price=json["fix"],
            total_price=json["total"],
            starts_at=datetime.datetime.fromisoformat(json["startsAt"]),
        )


class EwsApi:
    """Main API class"""
    _session: httpx.AsyncClient
    _data: list[PriceData]
    _meta: MetaData | None

    @classmethod
    async def authenticate(cls, api_key: str) -> bool:
        """Authenticate with the EWS API using the provided API key."""
        try:
            r = httpx.get(EWS_DATA_URI, headers={"X-API-KEY": api_key})
            return r.is_success
        except httpx.HTTPError:
            return False
    
    def __init__(self, api_key: str) -> None:
        """Initialize the EWS API client."""
        self._session = httpx.AsyncClient()
        self._session.headers.update({"User-Agent": build_user_agent()})
        self._session.headers.update({"X-API-KEY": api_key})
        self._data = []
        self._meta = None
    
    async def get(self) -> list[PriceData]:
        await self.fetch()
        return self._data

    async def get_raw_data(self) -> list[PriceData]:
        return list(self._data)
    
    async def fetch(self) -> bool:
        """Fetch data from the EWS API."""
        r = await self._session.get(EWS_DATA_URI)
        if not r.is_success:
            return False
        json_data: dict = r.json()
        
        self._meta = MetaData(
            interval=json_data["interval"],
            interval_unit=json_data["intervalUnit"],
            unit=json_data["priceUnit"],
            tariff=json_data["tariff"],
        )
        
        price_items = json_data.get("today", []) + json_data.get("tomorrow", [])
        self._data = [PriceData.from_json(item) for item in price_items]
        return True