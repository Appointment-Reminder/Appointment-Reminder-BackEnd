from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.config import config

from app.api.v1.jotform_Webhook import jotform_router
from app.api.v1.userRoutes import userRouter
from app.api.v1.appointment_routes import appointment_router
from app.api.v1.business_routes import business_router

app = FastAPI(title=config.app_name)

app.include_router(userRouter)
app.include_router(jotform_router)
app.include_router(appointment_router)
app.include_router(business_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:56779",     # Flutter web current port
        "http://localhost:5173",
        "https://app.yourdomain.com"
    ],
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

