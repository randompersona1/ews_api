from __future__ import annotations

import httpx

import ews_api
from ews_api.const import PROJECT_NAME, PROJECT_URL


def build_user_agent(version: str = ews_api.__version__) -> str:
    """Build a user agent string."""
    return f"{PROJECT_NAME}/{version} (+{PROJECT_URL}), httpx/{httpx.__version__}"
