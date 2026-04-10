from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name:str
    email:str
    password:str

class UserRead(BaseModel):
    id:int
    name:str
    email:str
    role:str

    class Config:
        from_attributes = True