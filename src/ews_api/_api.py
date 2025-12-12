from __future__ import annotations

import datetime
from dataclasses import dataclass

import httpx

from ._const import EWS_DATA_URI
from ._logging import logger
from ._utils import build_user_agent


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
    data: list[PriceData]
    meta: MetaData | None

    @classmethod
    async def authenticate(cls, api_key: str) -> bool:
        """Check whether the provided EWS API key is valid."""
        try:
            r = httpx.get(
                EWS_DATA_URI,
                headers={"User-Agent": build_user_agent(), "X-API-KEY": api_key},
            )
        except httpx.HTTPError:
            logger.error("Error creating authentication request")
            return False
        else:
            return r.is_success

    def __init__(self, api_key: str) -> None:
        """Initialize the EWS API client."""
        self._session = httpx.AsyncClient()
        self._session.headers.update({"User-Agent": build_user_agent()})
        self._session.headers.update({"X-API-KEY": api_key})
        self.data = []
        self.meta = None

    async def reauth(self, api_key: str) -> bool:
        """Reauthenticate the session with a new API key."""
        r = await EwsApi.authenticate(api_key)
        if r:
            self._session.headers.update({"X-API-KEY": api_key})
        return r

    async def fetch(self) -> bool:
        """Fetch data from the EWS API."""
        r = await self._session.get(EWS_DATA_URI)
        if not r.is_success:
            return False
        json_data: dict = r.json()

        self.meta = MetaData(
            interval=json_data["interval"],
            interval_unit=json_data["intervalUnit"],
            unit=json_data["priceUnit"],
            tariff=json_data["tariff"],
        )

        price_items = json_data.get("today", []) + json_data.get("tomorrow", [])
        self.data = [PriceData.from_json(item) for item in price_items]
        return True


def match_date(prices: list[PriceData], day: datetime.date) -> list[PriceData]:
    """Filter prices to have only those from a given day"""
    matches: list[PriceData] = []
    for price in prices:
        if price.starts_at.date() == day:
            matches.append(price)
    return matches


def get_price_now(prices: list[PriceData], time: datetime.datetime) -> float | None:
    """
    Return the total price whose start time is the closest lower value to ``time``.
    Function does not check that ``time`` is within any given timedelta of that start
    time.
    """
    if len(prices) < 2:
        return None

    lower: PriceData | None = None
    upper: datetime.datetime | None = None

    for price in prices:
        start = price.starts_at
        if start < time:
            if lower is None or start > lower.starts_at:
                lower = price
        elif start > time:
            if upper is None or start < upper:
                upper = start

    if lower is None or upper is None:
        return None
    return lower.total_price
