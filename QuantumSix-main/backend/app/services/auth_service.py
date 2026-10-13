from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.records import User
from app.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    def register_user(self, db: Session, username: str, password: str) -> dict:
        normalized = username.strip()
        if not normalized:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username is required.')
        if db.query(User).filter(User.username == normalized).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists.')
        user = User(username=normalized, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(user.username)
        return {'access_token': token, 'token_type': 'bearer', 'user': {'id': user.id, 'username': user.username}}

    def login_user(self, db: Session, username: str, password: str) -> dict:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password.')
        token = create_access_token(user.username)
        return {'access_token': token, 'token_type': 'bearer', 'user': {'id': user.id, 'username': user.username}}


auth_service = AuthService()
