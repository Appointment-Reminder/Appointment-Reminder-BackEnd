from typing import Iterator

from dishka import Provider, Scope, provide
from sqlalchemy.testing import future
from sqlmodel import SQLModel, create_engine, Session

from app.domain.core.config import config, Config

class Infrastructure(Provider):
    scope = Scope.APP

    @provide(Scope=Scope.APP)
    def get_config(self) -> Config:
        return config;

    @provide(Scope=Scope.APP)
    def get_engine(self, cfg: Config) -> SQLModel:
        return create_engine(cfg.db_url, echo=cfg.debug, future= True)

class DbProvider(Provider):
    scope = Scope.REQUEST

    @provide(Scope=Scope.APP)
    def get_session(self, engine) -> Iterator[Session]:
        with Session(engine) as session:
            yield session