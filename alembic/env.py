from logging.config import fileConfig

from alembic import context
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import SQLModel
from app.adapters.sql_model_adapter.user.models.user import User
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember
from app.adapters.sql_model_adapter.business.models.member_commission import MemberCommission
from app.adapters.sql_model_adapter.package.models.package import Package
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory
from app.adapters.sql_model_adapter.business.models.business import Business
from app.adapters.sql_model_adapter.jotform.models.jotform import JotformForm, JotformCredential
from app.domain.core.config import config


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine
    from app.domain.core.config import config

    connectable = create_engine(config.db_url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
