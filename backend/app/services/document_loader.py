from pydantic import EmailStr
from fastapi import HTTPException,File,UploadFile
import tempfile
import os
from app.services.database import DatabaseService
from langchain_docling.loader import DoclingLoader

import logging


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

db_service=DatabaseService()
class DocumentService():

    async def save_file_to_db(self,email:EmailStr,thread_id:str,file:UploadFile):
        try:

            filename=file.filename

            temp_path=os.path.join(tempfile.gettempdir(),filename)
            file_bytes=await file.read()

            with open(temp_path,"wb") as f:
                f.write(file_bytes)
            loader=DoclingLoader(file_path=temp_path)
            docs=loader.load()
            

            logger.info(f"docs loaded {docs}")


            
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Error in saving file to db function {e}"
            )


        