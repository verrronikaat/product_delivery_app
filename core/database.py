import os

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://appuser:apppassword@127.0.0.1:5433/delivery_db",
)

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Создаёт таблицы, если их нет."""
    from core import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """Генератор сессии для FastAPI Depends и для десктопа."""
    with Session(engine) as session:
        yield session