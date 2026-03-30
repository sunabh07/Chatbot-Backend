from sqlmodel import Field,SQLModel
from sqlalchemy import Column
from typing import Optional,List,Dict
import uuid 
from pydantic import EmailStr
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.dialects.postgresql import JSONB


class Document(SQLModel,table=True):
    __tablename__="documents"

    id:Optional[int]=Field(default=None,primary_key=True) 
    filename:str=Field(description="FUll name")
    thread_id:str=Field(default_factory=lambda:str(uuid.uuid4()),index=True)
    content:str
    embedding: Optional[List[float]] = Field(default=None,sa_type=VECTOR(3072))
    meta: Optional[Dict] = Field(default=None,sa_column=Column(JSONB))