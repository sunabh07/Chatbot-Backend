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
    
    async def save_document(self, email, thread_id, chunks, embeddings, filename):
        try:
            with Session(self.engine) as session:

                if len(chunks) != len(embeddings):
                    raise HTTPException(
                        status_code=400,
                        detail="Chunks and embeddings length mismatch"
                    )

                documents = []

                for chunk, emb in zip(chunks, embeddings):

                    if not chunk.page_content.strip():
                        continue

                    doc = Document(
                        filename=filename,
                        thread_id=thread_id,
                        content=chunk.page_content,
                        embedding=emb,
                        meta={
                            "page": chunk.metadata.get("page_number"),
                            "source": chunk.metadata.get("source"),
                            "type": chunk.metadata.get("category")
                        }
                    )

                    documents.append(doc)

                session.add_all(documents)
                session.commit()
                

                return {
                    "status": True,
                    "inserted": len(documents)
                }

        except Exception as e:
            logger.error(f"Error saving documents: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"DB Error: {e}"
            )
    def fetch_documents(self,query_embedding,thread_id):
        with Session(self.engine) as session:
            results = session.exec(

                select(Document)
                .where(Document.thread_id == thread_id)
                .where(Document.embedding.cosine_distance(query_embedding) < 0.4)  # threshold
                .order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(20)  # top K
            ).all()

            logger.info(f"retrieved docs for our vector search len(results)")

            return results
