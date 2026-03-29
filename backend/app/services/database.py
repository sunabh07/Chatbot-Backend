import os
from dotenv import load_dotenv
from sqlmodel import SQLModel,Session,create_engine,select
from fastapi import HTTPException,status
from pydantic import EmailStr
from app.models.user import User
from app.models.document import Document
import logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

load_dotenv()

class DatabaseService():
    def __init__(self):
        try:
            DATABASE_URL=os.getenv("POSTGRES_URL")

            logger.info("Creating engine")
            self.engine=create_engine(DATABASE_URL,echo=True,future=True)
            logger.info("Engine created")
            SQLModel.metadata.create_all(self.engine)
            logger.info("Tables created")
        except Exception as e:
            logger.error(f"Error occured during initialising Database Service::{e}")
    async def add_user(self,email:EmailStr,password:str,full_name:str):
        with Session(self.engine) as session:
            user= User(email=email,password=password,full_name=full_name)
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info("User added successfully")

            return user

    async def fetch_user(self,email:EmailStr,password:str):
        with Session(self.engine) as session:
            user=session.exec(
                select(User).where(User.email==email,User.password==password)
                ).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
    async def fetch_thread(self,email:EmailStr):
        with Session(self.engine) as session:
            user=session.exec(
                select(User).where(User.email==email)
                ).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user.thread_id
    