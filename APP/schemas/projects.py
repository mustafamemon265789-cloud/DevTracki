from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    name:str
    description:Optional[str]= None
    status: str = "active"

class ProjectRead(BaseModel):
    id:int
    name:str
    description:Optional[str]
    status:str
    owner_id: int

    class Config:
        from_attributes = True

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    