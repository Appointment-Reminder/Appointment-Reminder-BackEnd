from typing import Iterator

from dishka import Provider, Scope, provide
from sqlalchemy import Engine
from sqlalchemy.testing import future
from sqlmodel import SQLModel, create_engine, Session

from app.domain.core.config import config, Config

class Infrastructure(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return config;

    @provide(scope=Scope.APP)
    def get_engine(self, cfg: Config) -> Engine:
        return create_engine(cfg.db_url, echo=cfg.debug, future= True)

class DbProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_session(self, engine: Engine) -> Iterator[Session]:
        with Session(engine) as session:
            yield session