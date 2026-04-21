from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from schemas.auth import RegisterSchema, LoginSchema, ForgotPasswordSchema
from services.auth_service import register_user, login_user, forgot_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    return register_user(db, data.full_name, data.email, data.password)


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    return login_user(db, data.email, data.password)


@router.post("/forgot-password")
def forgot(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    return forgot_password(db, data.email)