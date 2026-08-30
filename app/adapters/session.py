from sqlmodel import create_engine, SQLModel, Session
from app.domain.core.config import config
from app.adapters.sql_model_adapter import *

engine = create_engine(
    config.db_url,
    echo=config.debug,
    future=True,
)

def get_session() -> SQLModel:
    with Session(engine) as session:
        yield session