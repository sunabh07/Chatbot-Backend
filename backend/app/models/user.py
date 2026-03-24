from sqlmodel import Field,SQLModel
from typing import Optional
import uuid 
from pydantic import EmailStr

class User(SQLModel,table=True):
    __tablename__="users"

    id:Optional[int]=Field(default=None,primary_key=True)
    email:EmailStr=Field(unique=True,index=True)
    password:str=Field(description="Password of the user")
    full_name:str=Field(description="FUll name")
    thread_id:str=Field(default_factory=lambda:str(uuid.uuid4()),unique=True,index=True)
