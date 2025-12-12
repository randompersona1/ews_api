"""ews_api package initialization."""

from importlib.metadata import PackageNotFoundError, version

from ._logging import logger
from .api import EwsApi, Metadata, PriceData, get_price_now, match_date


def _get_version() -> str:
    try:
        return version(__name__)
    except PackageNotFoundError:
        logger.debug("version unknown")
        return "0.0.0"


__version__ = _get_version()


__all__ = [
    "EwsApi",
    "Metadata",
    "PriceData",
    "__version__",
    "get_price_now",
    "match_date",
]
