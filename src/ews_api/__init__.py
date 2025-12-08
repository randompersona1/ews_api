from importlib.metadata import version, PackageNotFoundError

def _get_version() -> str:
    try:
        return version(__name__)
    except PackageNotFoundError:
        return "0.0.0"

__version__ = _get_version()