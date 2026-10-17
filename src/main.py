import threading

from fastapi import FastAPI, HTTPException, status

from .models import *

app = FastAPI(title="Service Registry")


_services: dict[UUID, ServiceOut] = {}
_lock = threading.Lock()


def _key(s: ServiceIn) -> tuple[str, int]:
    return (s.host, s.port)


@app.post(
    "/services",
    response_model=AddServicesResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_services(req: AddServicesRequest):
    with _lock:
        existing = {_key(s) for s in _services.values()}
        seen: set[tuple[str, int]] = set()

        # Validate the whole batch first, so it's all-or-nothing
        for s in req.services:
            k = _key(s)
            if k in existing or k in seen:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Service at {s.host}:{s.port} already exists",
                )
            seen.add(k)

        created = [ServiceOut(id=uuid4(), **s.model_dump()) for s in req.services]
        for s in created:
            _services[s.id] = s

    return AddServicesResponse(services=created)


@app.get("/services", response_model=list[ServiceOut])
def list_services():
    return list(_services.values())
