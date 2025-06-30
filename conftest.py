# em conftest.py
from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.db.session import Base, SessionLocal, engine


@pytest.fixture(scope="function")
def db_session() -> Generator[Session]:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
