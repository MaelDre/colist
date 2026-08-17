import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("COLIST_DATABASE_URL", "sqlite:///./colist.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _drop_leftover_description_column() -> None:
    # Databases created before the `description` column was removed from
    # the `Item` model still have it as `NOT NULL` with no DB-level default,
    # so leaving it in place breaks every insert once the ORM stops
    # populating it. `create_all` never alters existing tables, so this has
    # to be dropped explicitly; safe to run on every startup since it's a
    # no-op once the column is gone.
    with engine.begin() as conn:
        columns = {row[1] for row in conn.execute(text("PRAGMA table_info(items)"))}
        if "description" in columns:
            conn.execute(text("ALTER TABLE items DROP COLUMN description"))


def init_db() -> None:
    from app import models  # noqa: F401  (ensure models are registered on Base)

    Base.metadata.create_all(bind=engine)
    _drop_leftover_description_column()
