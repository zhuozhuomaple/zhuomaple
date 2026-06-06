from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from sqlalchemy import inspect

    from app import models  # noqa: F401

    expected_columns = {col.name for col in models.Task.__table__.columns}
    inspector = inspect(engine)
    if inspector.has_table("tasks"):
        actual_columns = {col["name"] for col in inspector.get_columns("tasks")}
        if actual_columns != expected_columns:
            Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
