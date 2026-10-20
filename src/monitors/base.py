import asyncio
import contextlib
import socket
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["up", "down"]


@dataclass
class MonitorResult:
    status: Status
    response_time_ms: float | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


# Signature every protocol monitor implements: (host, port, timeout) -> MonitorResult
ProtocolMonitor = Callable[[str, int, float], Awaitable[MonitorResult]]


def up(start: float, **details: Any) -> MonitorResult:
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    return MonitorResult("up", elapsed, details=details)


def down(error: str, **details: Any) -> MonitorResult:
    return MonitorResult("down", error=error, details=details)


def describe_error(e: BaseException, timeout: float) -> str:
    # TimeoutError, ConnectionRefusedError and gaierror are all OSError subclasses: check them first
    if isinstance(e, TimeoutError):
        return f"Timed out after {timeout}s"
    if isinstance(e, ConnectionRefusedError):
        return "Connection refused"
    if isinstance(e, socket.gaierror):
        return f"DNS resolution failed: {e}"
    return str(e) or type(e).__name__


async def close_writer(writer: asyncio.StreamWriter) -> None:
    writer.close()
    with contextlib.suppress(Exception):
        await writer.wait_closed()
