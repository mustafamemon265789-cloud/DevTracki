from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime 
class ProjectBase(SQLModel):
    name:str
    description:Optional[str] = None
    status:str = Field(default = "active")
class Project(ProjectBase, table = True):
    id: Optional[int] = Field(default=None,primary_key=True)
    owner_id : int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory = datetime.utcnow)    

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id:int
    owner_id:int
    created_at:datetime
    