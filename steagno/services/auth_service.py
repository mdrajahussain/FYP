from sqlalchemy.orm import Session
from models.user import User
from core.security import hash_password, verify_password, create_token


def register_user(db: Session, full_name: str, email: str, password: str):

    if not full_name or not email or not password:
        return {"success": False, "message": "All fields are required"}

    user = db.query(User).filter(User.email == email).first()
    if user:
        return {"success": False, "message": "User already exists"}
    

    new_user = User(
        full_name=full_name,
        email=email,
        password=hash_password(password)
    )
    db.add(new_user)
    db.commit()

    return {"success": True, "message": "User registered"}


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return {"success": False, "message": "Invalid credentials"}

    user_response = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email
    }

    token = create_token({"sub": user.email})

    return {
        "success": True,
        "access_token": token,
        "data": user_response,
        "token_type": "bearer"
    }


def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}

    # simple version (no email sending yet)
    return {
        "success": True,
        "message": "will be added later: password reset link sent to email (not implemented)"
    }