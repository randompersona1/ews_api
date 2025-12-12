# ruff: noqa: S101
import re

import httpx

from ews_api._const import PROJECT_NAME, PROJECT_URL
from ews_api._utils import build_user_agent


def test_build_user_agent_defaults():
    user_agent = build_user_agent()
    assert PROJECT_NAME in user_agent
    assert PROJECT_URL in user_agent
    assert httpx.__version__ in user_agent


def test_build_user_agent_custom_values():
    r = re.compile(
        r"ews_api/1\.2\.3 \(\+https://github\.com/randompersona1/ews_api\), httpx/\d+\.\d+\.\d+"  # noqa: E501
    )
    user_agent = build_user_agent(version="1.2.3")
    assert r.match(user_agent)
