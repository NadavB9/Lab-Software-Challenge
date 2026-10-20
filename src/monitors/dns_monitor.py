import asyncio
import socket
import time

from .base import MonitorResult, describe_error, down, up


async def monitor_dns(host: str, port: int, timeout: float) -> MonitorResult:  # port unused
    """Up if the host resolves; details.addresses lists the resolved IPs."""
    start = time.perf_counter()
    loop = asyncio.get_running_loop()
    try:
        infos = await asyncio.wait_for(
            loop.getaddrinfo(host, None, type=socket.SOCK_STREAM), timeout
        )
    except Exception as e:
        return down(describe_error(e, timeout))
    return up(start, addresses=sorted({info[4][0] for info in infos}))


async def reverse_dns(ip: str, timeout: float) -> str | None:
    """Hostname for an IP via reverse lookup, or None."""
    loop = asyncio.get_running_loop()
    try:
        name, _ = await asyncio.wait_for(loop.getnameinfo((ip, 0), socket.NI_NAMEREQD), timeout)
        return name
    except Exception:
        return None
