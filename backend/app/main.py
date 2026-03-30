from fastapi import FastAPI,HTTPException,File,UploadFile,status,Depends,Body
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import EmailStr
from app.services.database import DatabaseService
import logging
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from app.services.verify_token import verify_token
import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from app.graph.message import process_message
from app.services.document_loader import DocumentService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


app=FastAPI()


db_service=DatabaseService()
doc_service=DocumentService()
conn = psycopg.connect(os.getenv("POSTGRES_URL"))
conn.autocommit = True   
memory=PostgresSaver(conn)
memory.setup()

@app.on_event("shutdown")
async def shutdown_event():
    if conn:
        conn.close()
        logger.info("Connection closed for checkpoint postgres")

@app.post("/register",description="Registering a new user")
async def register(email:EmailStr,password:str,full_name:str):
    logger.info("Inside register function")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Email parameter is required"
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password parameter is required"
        )
    if not full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The full_name parameter is required"
        )
    if len(password)<5:
          raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The length of password must be greater than 5"
        )
    
    result = await db_service.add_user(email,password,full_name)

    return result

@app.post("/login",description="Login in the user")
async def login(email:EmailStr,password:str):
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Email parameter is required"
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password parameter is required"
        )

    user=await db_service.fetch_user(email,password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user is not found"
        )
    token_data={
        "email":email,
        "exp":datetime.utcnow()+timedelta(hours=1)
        }
    token=jwt.encode(token_data,os.getenv("JWT_SECRET"),algorithm="HS256")
    return {
    "message":"User logged in successfully",
    "token":token
    }

@app.post("/ask",description="Asking queries with the AI")
async def ask_question(
    query:str=Body(...,embed=True),
    email:str=Depends(verify_token)
):
    logger.info("Inside asking query function")

    thread_id=await db_service.fetch_thread(email)

    result=process_message(memory,thread_id,query)

    if result["error"]:
        raise HTTPException(
            status_code=401,
            detail="Error occured during process message"
        )

    return {
        "answer":result["answer"]
    }

    
@app.post("/upload")
async def upload(file:UploadFile=File(...),email:EmailStr=Depends(verify_token)):
    if not file:
        raise HTTPException(
            status_code=401,
            detail="File is required in this field"
        )
    
    thread_id=await db_service.fetch_thread(email)
    try:
        x=await doc_service.save_file_to_db(email,thread_id,file)
        if x["status"]:
            return x
        else:
            return {"status":"Error in saving file"}

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Error occured during file upload: {e}"
        )
    



    

