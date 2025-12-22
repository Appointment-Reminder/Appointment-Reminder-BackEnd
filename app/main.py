from fastapi import FastAPI

from app.core.config import config

app = FastAPI(title=config.app_name)

@app.get("/")
def read_root():
    return {"Hello": "World"}
