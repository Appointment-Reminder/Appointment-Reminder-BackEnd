from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import config

engine = create_engine(
    config.db_url,
    echo=config.debug,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    )

