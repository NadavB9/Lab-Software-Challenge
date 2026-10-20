import time

import httpx

from .base import MonitorResult, describe_error, down, up


async def monitor_http(host: str, port: int, timeout: float) -> MonitorResult:
    """Up with details.status_code if any HTTP response comes back."""
    url_host = f"[{host}]" if ":" in host else host  # IPv6 literal
    url = f"http://{url_host}:{port}/"
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            resp = await client.get(url)
    except httpx.TimeoutException:
        return down(f"Timed out after {timeout}s", url=url)
    except httpx.HTTPError as e:
        return down(f"{type(e).__name__}: {e}", url=url)
    except Exception as e:
        return down(describe_error(e, timeout), url=url)
    return up(start, url=url, status_code=resp.status_code)
