from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.schemas.auth import TokenResponse, UserCreate, UserLogin
from app.utils.security import get_current_user

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    return services.auth_service.register_user(db, payload.username, payload.password)


@router.post('/login', response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    return services.auth_service.login_user(db, payload.username, payload.password)


@router.get('/me', response_model=dict)
def current_user(current_user=Depends(get_current_user)):
    return {'id': current_user.id, 'username': current_user.username}
