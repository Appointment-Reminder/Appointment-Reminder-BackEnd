from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.config import config

from app.api.v1.userRoutes import userRouter

app = FastAPI(title=config.app_name)

app.include_router(userRouter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173",   # Flutter web dev TODO Add the localhost flutter address
        "https://app.yourdomain.com"], #Production frontend], TODO Add the production frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def read_root():
    return JSONResponse(status_code=200, content={"status": "OK"})

