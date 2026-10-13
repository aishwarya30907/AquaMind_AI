from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db

router = APIRouter(prefix='/api', tags=['predictions'])


@router.get('/predictions/history')
def get_prediction_history(db: Session = Depends(get_db)):
    return services.prediction_service.get_history(db)
