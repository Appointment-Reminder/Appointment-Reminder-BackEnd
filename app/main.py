import uvicorn

from dishka import make_container
from dishka.integrations.fastapi import setup_dishka, FastapiProvider

from fastapi import FastAPI

from sqlmodel import SQLModel

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.Dependency.appointment import AppointmentProvider
from app.Dependency.business import BusinessProvider
from app.Dependency.infrastructure import Infrastructure, DbProvider
from app.Dependency.jotform import JotformProvider
from app.Dependency.package import PackageProvider
from app.Dependency.user import UserProvider

from app.domain.core.config import config

from app.api.v1.exception_handlers import register_exception_handlers
from app.api.v1.jotform_Webhook import jotform_router
from app.api.v1.userRoutes import userRouter
from app.api.v1.appointment_routes import appointment_router
from app.api.v1.business_routes import business_router
from app.adapters.session import engine

app = FastAPI(title=config.app_name)

container = make_container(
    Infrastructure(),
    DbProvider(),
    UserProvider(),
    BusinessProvider(),
    JotformProvider(),
    PackageProvider(),
    AppointmentProvider(),
    FastapiProvider(),
)
setup_dishka(container, app)

register_exception_handlers(app)
app.include_router(userRouter)
app.include_router(jotform_router)
app.include_router(appointment_router)
app.include_router(business_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:56779",     # Flutter web current port
        "http://localhost:5173",
        "http://localhost:9100",
        "http://127.0.0.1:9100",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    SQLModel.metadata.create_all(bind=engine)
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def read_root():
    return JSONResponse(status_code=200, content={"status": "OK"})

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")

