import logging

from .base import MonitorResult, ProtocolMonitor, Status, down
from .dns_monitor import monitor_dns
from .http_monitor import monitor_http, monitor_https
from .ssh_monitor import monitor_ssh
from .tcp_monitor import monitor_tcp

log = logging.getLogger(__name__)

# One monitor per monitor_type. Add new protocols here.
MONITORS: dict[str, ProtocolMonitor] = {
    "tcp": monitor_tcp,
    "http": monitor_http,
    "https": monitor_https,
    "ssh": monitor_ssh,
    "dns": monitor_dns,
}


async def run_monitor(monitor_type: str, host: str, port: int, timeout: float) -> MonitorResult:
    """Run the single monitor for this service's monitor_type. Never raises."""
    monitor = MONITORS.get(monitor_type)
    if monitor is None:
        return down(f"Unknown monitor type '{monitor_type}'")
    try:
        return await monitor(host, port, timeout)
    except Exception as e:  # monitors shouldn't raise, but never let one crash the caller
        log.exception("%s monitor crashed for %s:%s", monitor_type, host, port)
        return down(f"Monitor failed: {type(e).__name__}")


__all__ = ["MONITORS", "MonitorResult", "Status", "run_monitor"]
