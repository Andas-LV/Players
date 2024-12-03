import os
from datetime import datetime, timedelta
import boto3
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

import models
from database import get_db

from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME,
)

def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded token payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise HTTPException(
            status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {e}")
        raise HTTPException(
            status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}
            )
        user = get_user_by_username(db, username)
        if user is None:
            raise HTTPException(
                status_code=404, detail="User not found"
            )
        return user
    except HTTPException as e:
        raise e
def get_user_by_username(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def upload_to_s3(file_obj, bucket_name, object_name):
    try:
        s3_client.upload_fileobj(file_obj, bucket_name, object_name, ExtraArgs={"ACL": "public-read"})
        file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{object_name}"
        return file_url
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Ошибка авторизации AWS")
