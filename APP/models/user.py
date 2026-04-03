from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    name:str
    email:str
    role:str =Field(default="Developer")

class User(UserBase, table = True):
    id :Optional [int] = Field(default=None, primary_keys=True)
    hashed_password:str
    created_at:datetime = Field(default_factory=datetime.utnow)

class UserCreate(UserBase):
    password:str

class UserRead(UserBase):
    id:int
    created_at:datetime