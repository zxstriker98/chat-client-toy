from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.Base import Base


def create_db(db_path: str = ":memory:"):
    url = "sqlite://" if db_path == ":memory:" else f"sqlite:///{db_path}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)