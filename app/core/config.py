import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Config(BaseSettings):
    app_name: str = "Photographer-SAAs"
    debug: bool = False
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""

    @property
    def db_url(self):
        return  ##//TODO connect to postgresql db

config = Config();