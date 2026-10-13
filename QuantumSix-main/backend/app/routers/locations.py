from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.records import LocationObservation

router = APIRouter(prefix='/api', tags=['locations'])


@router.get('/locations')
def list_locations(db: Session = Depends(get_db)):
    records = db.query(LocationObservation).order_by(LocationObservation.timestamp.desc()).all()
    return {
        'status': 'ok',
        'locations': [
            {
                'id': record.id,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'timestamp': record.timestamp.isoformat(),
                'hab_risk': record.hab_risk,
                'plankton_observation': record.plankton_observation,
                'sensor_observation': record.sensor_observation,
            }
            for record in records
        ],
    }
