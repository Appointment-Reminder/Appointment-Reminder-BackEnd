from typing import Optional

from pydantic import BaseModel

class Photographer(BaseModel):
    id: Optional[str]
    name: str
    email: Optional[str]
    phone: Optional[str] = None