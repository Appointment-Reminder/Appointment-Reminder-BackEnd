from fastapi import APIRouter
from typing import List
from app.models.photographer import Photographer


router = APIRouter(prefix="/photographers", tags=["photographers"])

# Dummy in-memory storage
photographers_db = {
    "1": Photographer(id="1", name="Photog A", email="a@example.com"),
    "2": Photographer(id="2", name="Photog B", email="b@example.com")
}

@router.get("/", response_model=List[Photographer])
def list_photographers():
    return list(photographers_db.values())

