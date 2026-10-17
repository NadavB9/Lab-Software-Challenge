from uuid import UUID, uuid4

from pydantic import BaseModel, Field, IPvAnyAddress


class ServiceIn(BaseModel):
    name: str = Field(min_length=1)
    host: IPvAnyAddress = Field(min_length=1)
    port: int = Field(ge=1, le=65535)


class ServiceOut(ServiceIn):
    id: UUID


class AddServicesRequest(BaseModel):
    services: list[ServiceIn] = Field(min_length=1)


class AddServicesResponse(BaseModel):
    services: list[ServiceOut]
