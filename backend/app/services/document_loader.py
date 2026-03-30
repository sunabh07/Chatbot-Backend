from pydantic import EmailStr
from fastapi import HTTPException,File,UploadFile
import tempfile
import os
from app.services.database import DatabaseService
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.graph.base import client



import logging


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

db_service=DatabaseService()
class DocumentService():

    async def save_file_to_db(self,email:EmailStr,thread_id:str,file:UploadFile):
        logger.info("Inside save_file_to_db function")
        try:

            filename=file.filename

            temp_path=os.path.join(tempfile.gettempdir(),filename)
            file_bytes=await file.read()

            with open(temp_path,"wb") as f:
                f.write(file_bytes)

            
            loader=UnstructuredPDFLoader(file_path=temp_path,mode="elements")
            docs=loader.load()
            logger.info(f"docs loaded {docs}")            

            chunks=self.chunker(docs)

            content = "\n".join(chunk.page_content for chunk in chunks)

            logger.info(f"This is the total content of the docs:::::: {content}")

            logger.info(f"chunks loaded {chunks[0].page_content}")

            embeddings=await self.doc_embeddings(chunks)
            logger.info("Embeddings created")

            save=await db_service.save_document(email,thread_id,chunks,embeddings,filename)
            
            os.remove(temp_path)
            return save
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Error in saving file to db function {e}"
            )


    async def doc_embeddings(self,chunks):

        texts = [chunk.page_content for chunk in chunks if chunk.page_content.strip()]
        logger.info("texts are created from chunks")
        result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=texts
    )
        logger.info("Embeddings created for texts")
        embeddings = [e.values for e in result.embeddings]
        logger.info(f"Embeddings are :::: {embeddings}")

        print(len(result.embeddings[0].values))
        return embeddings

    def chunker(self,docs):

        splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

        chunks = splitter.split_documents(docs)

        return chunks
