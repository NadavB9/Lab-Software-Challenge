import asyncio
import time

from .base import MonitorResult, close_writer, describe_error, down, up


async def monitor_tcp(host: str, port: int, timeout: float) -> MonitorResult:
    """Up if a TCP connection to host:port succeeds."""
    start = time.perf_counter()
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    except Exception as e:
        return down(describe_error(e, timeout))
    result = up(start)
    await close_writer(writer)
    return result
