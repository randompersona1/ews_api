"""ews_api package initialization."""

from importlib.metadata import PackageNotFoundError, version


def _get_version() -> str:
    try:
        return version(__name__)
    except PackageNotFoundError:
        return "unknownversion"


__version__ = _get_version()
