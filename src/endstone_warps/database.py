from pathlib import Path

from sqlalchemy import Column, Float, Integer, MetaData, Table, Text, create_engine, text
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