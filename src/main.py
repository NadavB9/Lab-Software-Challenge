from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Request, status
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.exc import IntegrityError

from .models import AddServicesRequest, Service
from .service_repository import ServiceRepository, create_services_table, init_engine


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_backend: Literal["sqlite", "postgres"] = "sqlite"
    db_name: str = "services.db"
    db_user: str = ""
    db_password: SecretStr = SecretStr("")
    db_host: str = "localhost"
    db_port: int = 5432


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = init_engine(
        db_name=settings.db_name,
        backend=settings.db_backend,
        user=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
    )
    table = create_services_table(engine)
    app.state.repo = ServiceRepository(engine, table)
    yield
    engine.dispose()


app = FastAPI(title="Service Registry", lifespan=lifespan)


def get_repo(request: Request) -> ServiceRepository:
    return request.app.state.repo


RepoDep = Annotated[ServiceRepository, Depends(get_repo)]


@app.post(
    "/services",
    response_model=list[Service],
    status_code=status.HTTP_201_CREATED,
)
def add_services(req: AddServicesRequest, repo: RepoDep):
    keys = [(s.host, s.port) for s in req.services]
    if len(set(keys)) != len(keys):
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicate host:port in request")

    try:
        return repo.add_many(s.model_dump() for s in req.services)
    except IntegrityError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "One or more services already exist"
        )


@app.get("/services", response_model=list[Service])
def list_services(repo: RepoDep):
    return repo.list_all()


@app.get("/services/{service_id}", response_model=Service)
def get_service(service_id: int, repo: RepoDep):
    svc = repo.get(service_id)
    if svc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found")
    return svc


@app.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, repo: RepoDep):
    if not repo.delete(service_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found")
