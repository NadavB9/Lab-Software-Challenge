import asyncio
import time

from .base import MonitorResult, close_writer, describe_error, down, up
from .dns_monitor import reverse_dns


async def _read_banner(reader: asyncio.StreamReader, max_lines: int = 10) -> str | None:
    # RFC 4253: the server may send other lines before the "SSH-" identification line
    for _ in range(max_lines):
        line = await reader.readline()
        if not line:
            return None
        text = line.decode("utf-8", "replace").strip()
        if text.startswith("SSH-"):
            return text
    return None


async def monitor_ssh(host: str, port: int, timeout: float) -> MonitorResult:
    """Up with details.hostname and details.banner if an SSH server answers."""
    start = time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    except Exception as e:
        return down(describe_error(e, timeout))

    try:
        banner = await asyncio.wait_for(_read_banner(reader), timeout)
        peer_ip = writer.get_extra_info("peername")[0]
    except Exception as e:
        return down(f"No SSH banner: {describe_error(e, timeout)}")
    finally:
        await close_writer(writer)

    if banner is None:
        return down("Not an SSH server (no SSH- banner received)")

    result = up(start, ip=peer_ip, banner=banner)
    result.details["hostname"] = await reverse_dns(peer_ip, timeout) or host
    return result
