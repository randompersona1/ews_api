from __future__ import annotations

from ews_api.const import PROJECT_NAME, PROJECT_URL

import httpx


def build_user_agent(name: str = PROJECT_NAME, version: str = "0.0.0") -> str:
    """Build a user agent string."""
    return f"{name}/{version} (+{PROJECT_URL}), httpx/{httpx.__version__}"
