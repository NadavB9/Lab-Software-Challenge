from datetime import datetime

from pydantic import BaseModel, Field


class ServiceIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)


class Service(ServiceIn):
    id: int
    status: str
    last_checked: datetime | None = None
    response_time_ms: float | None = None


class AddServicesRequest(BaseModel):
    services: list[ServiceIn] = Field(min_length=1)
