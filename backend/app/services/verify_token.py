import os
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException,File,UploadFile,status,Depends,Body
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
import jwt

load_dotenv()




security=HTTPBearer()

def verify_token(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token=credentials.credentials
    try:
        payload=jwt.decode(token,os.getenv("JWT_SECRET"),algorithms=["HS256"])
        email=payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The Email not found"
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="token is expired")
    except Exception as e:
        raise HTTPException(status_code=401,detail=f"invalid token, {e}")
    