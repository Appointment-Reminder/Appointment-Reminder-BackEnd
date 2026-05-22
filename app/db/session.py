import sqlmodel
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import config
from app.db.models import *

engine = create_engine(
    config.db_url,
    echo=config.debug,
    future=True,
)

def get_session() -> SQLModel:
    with Session(engine) as session:
        yield session