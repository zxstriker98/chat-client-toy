from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from database.Base import Base


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key enforcement for SQLite connections."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db(db_path: str = ":memory:"):
    url = "sqlite://" if db_path == ":memory:" else f"sqlite:///{db_path}"
    engine = create_engine(url)
    event.listen(engine, "connect", _set_sqlite_pragma)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)