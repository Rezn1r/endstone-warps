from pathlib import Path

from sqlalchemy import Column, Float, Integer, MetaData, Table, Text, create_engine, select, text
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

metadata = MetaData()

warps = Table(
    "warps",
    metadata,
    Column("uuid", Text, primary_key=True),
    Column("world", Text, nullable=False),
    Column("x", Float, nullable=False),
    Column("y", Float, nullable=False),
    Column("z", Float, nullable=False),
    Column("yaw", Float, nullable=True, server_default=text("0")),
    Column("pitch", Float, nullable=True, server_default=text("0")),
    Column("creator", Text, nullable=True),
    Column("created_at", Integer, nullable=True),
)


def initialize_database(data_folder: str | Path) -> Engine:
    database_folder = Path(data_folder)
    database_folder.mkdir(parents=True, exist_ok=True)

    database_path = (database_folder / "warps.db").as_posix()
    engine = create_engine(f"sqlite:///{database_path}")
    metadata.create_all(engine)
    return engine


def get_warp(engine: Engine, warp_name: str):
    with engine.connect() as connection:
        return connection.execute(select(warps).where(warps.c.uuid == warp_name)).mappings().first()


def list_warps(engine: Engine):
    with engine.connect() as connection:
        return connection.execute(select(warps).order_by(warps.c.uuid.asc())).mappings().all()


def save_warp(
    engine: Engine,
    warp_name: str,
    world: str,
    x: float,
    y: float,
    z: float,
    yaw: float,
    pitch: float,
    creator: str | None,
    created_at: int | None,
) -> None:
    statement = sqlite_insert(warps).values(
        uuid=warp_name,
        world=world,
        x=x,
        y=y,
        z=z,
        yaw=yaw,
        pitch=pitch,
        creator=creator,
        created_at=created_at,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[warps.c.uuid],
        set_={
            "world": world,
            "x": x,
            "y": y,
            "z": z,
            "yaw": yaw,
            "pitch": pitch,
            "creator": creator,
            "created_at": created_at,
        },
    )

    with engine.begin() as connection:
        connection.execute(statement)


def delete_warp(engine: Engine, warp_name: str) -> bool:
    with engine.begin() as connection:
        result = connection.execute(warps.delete().where(warps.c.uuid == warp_name))
    return result.rowcount > 0