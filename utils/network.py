"""HTTP client helpers."""

from httpx import Client
from .config import PROXY_HOST, PROXY_PORT


def get_proxy_client() -> Client:
    """Return an httpx.Client using proxy settings when configured."""
    if PROXY_HOST and PROXY_PORT:
        return Client(proxies=f"http://{PROXY_HOST}:{PROXY_PORT}")
    return Client()

