import time

import httpx

from .base import MonitorResult, describe_error, down, up


def build_url(scheme: str, host: str, port: int) -> str:
    url_host = f"[{host}]" if ":" in host else host  # IPv6 literal
    return f"{scheme}://{url_host}:{port}/"


async def request_url(url: str, timeout: float, verify: bool = True) -> MonitorResult:
    """GET the URL. Up with details.status_code if any HTTP response comes back."""
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False, verify=verify) as client:
            resp = await client.get(url)
    except httpx.TimeoutException:
        return down(f"Timed out after {timeout}s", url=url)
    except httpx.HTTPError as e:
        return down(f"{type(e).__name__}: {e}", url=url)
    except Exception as e:
        return down(describe_error(e, timeout), url=url)
    return up(start, url=url, status_code=resp.status_code)


async def monitor_http(host: str, port: int, timeout: float) -> MonitorResult:
    return await request_url(build_url("http", host, port), timeout)

async def monitor_https(host: str, port: int, timeout: float) -> MonitorResult:
    return await request_url(build_url("https", host, port), timeout, verify=True)
