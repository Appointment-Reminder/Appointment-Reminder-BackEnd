from fastapi import APIRouter
from typing import List
from app.models.photographer import Photographer
from app.Database.client import photographers_col
from fastapi import HTTPException

router = APIRouter(prefix="/photographers", tags=["photographers"])

@router.get("/", response_model=List[Photographer])
async def list_photographers():
    docs = await photographers_col.find().to_list(100)
    return docs

@router.get("/{photographer_id}", response_model=Photographer)
async def get_photographer(photographer_id: str):
    doc = await photographers_col.find_one({"_id": photographer_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Photographer not found")
    return doc

