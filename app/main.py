import uvicorn
from fastapi import FastAPI
from app.routes import appointments, reminders, photographers

app = FastAPI(title="Photo Reminder API")

# Include routers
app.include_router(appointments.router)
app.include_router(reminders.router)
app.include_router(photographers.router)

@app.get("/")
def root():
    return {"message": "Hello Photo Reminder"}