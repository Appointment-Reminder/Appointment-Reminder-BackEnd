# tests/conftest.py
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from app.adapters.sql_model_adapter import *  # noqa — registers all table models with SQLModel.metadata
import os

# Explicitly import every SQLModel table so metadata is fully populated
# before create_all runs. The package __init__.py files are empty, so
# nothing gets registered unless imported directly here.
from app.adapters.sql_model_adapter.user.models.user import User
from app.adapters.sql_model_adapter.business.models.business import Business
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember
from app.adapters.sql_model_adapter.business.models.member_commission import MemberCommission
from app.adapters.sql_model_adapter.package.models.package import Package
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment
from app.adapters.sql_model_adapter.jotform.models.jotform import (
    JotformCredential, JotformForm, JotformFormAssignment,
)
from app.adapters.sql_model_adapter.jotform.models.jotform_field_mapping import JotformFieldMapping


load_dotenv(dotenv_path=".env.test", override=True)
TEST_DB_URL = (
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, echo=False, future=True)
    SQLModel.metadata.create_all(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()