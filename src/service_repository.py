from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    Engine,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent

metadata = MetaData()

services_table = Table(
    "services",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False, unique=True),
    Column("host", String(255), nullable=False),
    Column("port", Integer, nullable=False),
    Column("monitor_type", String(10), nullable=False, server_default="tcp"),
    Column("status", String(20), nullable=False, server_default="unknown"),
    Column("last_monitored", DateTime(timezone=True), nullable=True),
    Column("response_time_ms", Float, nullable=True),
    Column("error", String(500), nullable=True),
    Column("details", JSON, nullable=True),
    CheckConstraint("port BETWEEN 1 AND 65535", name="ck_services_port_range"),
)


def init_engine(
    db_name: str,
    backend: str = "sqlite",
    user: str = "",
    password: str = "",
    host: str = "",
    port: int = 5432,
) -> Engine:
    if backend == "sqlite":
        return create_engine(f"sqlite:///{BASE_DIR / db_name}")

    if backend == "postgres":
        if not all([db_name, user, password, host, port]):
            raise ValueError(
                "db_name, user, password, host and port are required for postgres"
            )
        url = URL.create(
            "postgresql+psycopg",
            username=user,
            password=password,  # escaped automatically
            host=host,
            port=port,
            database=db_name,
        )
        return create_engine(url, pool_pre_ping=True)

    raise NotImplementedError(f"DB backend {backend!r} is not implemented yet")


def create_services_table(engine: Engine) -> Table:
    """Create the services table if it doesn't already exist (no-op otherwise)."""
    metadata.create_all(engine, tables=[services_table], checkfirst=True)
    return services_table


class ServiceRepository:
    def __init__(self, engine: Engine, table: Table = services_table) -> None:
        self.engine = engine
        self.table = table

    def add_many(self, services: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        """Insert several services in one transaction and return the created rows."""
        rows = [dict(s) for s in services]
        if not rows:
            return []
        stmt = insert(self.table).returning(*self.table.c, sort_by_parameter_order=True)
        with self.engine.begin() as conn:
            return [dict(r) for r in conn.execute(stmt, rows).mappings()]

    def get(self, service_id: int) -> dict[str, Any] | None:
        stmt = select(self.table).where(self.table.c.id == service_id)
        with self.engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()
            return dict(row) if row else None

    def list_all(self) -> list[dict[str, Any]]:
        stmt = select(self.table).order_by(self.table.c.id)
        with self.engine.connect() as conn:
            return [dict(row) for row in conn.execute(stmt).mappings()]

    def delete(self, service_id: int) -> bool:
        stmt = delete(self.table).where(self.table.c.id == service_id)
        with self.engine.begin() as conn:
            return conn.execute(stmt).rowcount > 0

    def update_monitor_result(
        self,
        service_id: int,
        status: str,
        last_monitored: datetime,
        response_time_ms: float | None,
        error: str | None,
        details: dict[str, Any] | None,
    ) -> bool:
        stmt = (
            update(self.table)
            .where(self.table.c.id == service_id)
            .values(
                status=status,
                last_monitored=last_monitored,
                response_time_ms=response_time_ms,
                error=error[:500] if error else None,
                details=details,
            )
        )
        with self.engine.begin() as conn:
            return conn.execute(stmt).rowcount > 0
