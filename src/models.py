import ipaddress
import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ServiceStatus = Literal["unknown", "up", "down"]
MonitorType = Literal["tcp", "http", "https", "ssh", "dns"]

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


class ServiceIn(BaseModel):
    """A service as submitted by the client."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    host: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)
    monitor_type: MonitorType = "tcp"

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        if not _HOSTNAME_RE.match(v):
            raise ValueError("must be a valid IP address or hostname")
        return v


class Service(BaseModel):
    """A stored service, including its latest monitoring result."""

    id: int
    name: str
    host: str
    port: int
    monitor_type: MonitorType
    status: ServiceStatus
    last_monitored: datetime | None = None
    response_time_ms: float | None = None
    error: str | None = None
    details: dict[str, Any] | None = None


class AddServicesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    services: list[ServiceIn] = Field(min_length=1)
