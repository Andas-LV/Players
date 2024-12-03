import os
from dotenv import load_dotenv
import boto3
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import schemas
import auth
from database import get_db
import models

load_dotenv()

router = APIRouter()

AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

@router.get("/user/me", response_model=schemas.UserInDB)
async def user_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.post("/register", response_model=schemas.UserInDB)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
async def login_user(form_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = auth.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access": access_token, "token_type": "bearer"}

@router.put("/user/update-avatar/", response_model=schemas.UserInDB)
async def update_avatar(
    avatar: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    object_name = f"avatars/{current_user.id}/{avatar.filename}"

    try:
        file_url = auth.upload_to_s3(avatar.file, AWS_STORAGE_BUCKET_NAME, object_name)

        current_user.avatar_url = file_url
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")