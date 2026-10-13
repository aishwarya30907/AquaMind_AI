from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.records import SensorReading
from app.schemas.sensor import SensorInput

router = APIRouter(prefix='/api/sensors', tags=['sensors'])


@router.post('/data')
def create_sensor_data(payload: SensorInput, db: Session = Depends(get_db)):
    record = SensorReading(
        temperature=payload.temperature,
        salinity=payload.salinity,
        ph=payload.ph,
        dissolved_oxygen=payload.dissolved_oxygen,
        chlorophyll=payload.chlorophyll,
        nitrate=payload.nitrate,
        turbidity=payload.turbidity,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {'status': 'ok', 'message': 'Sensor data stored successfully.', 'record': {'id': record.id, 'timestamp': record.timestamp.isoformat()}}


@router.get('/latest')
def get_latest_sensor_data(db: Session = Depends(get_db)):
    latest = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).first()
    if latest is None:
        return {'status': 'no-data', 'reading': None}
    return {
        'status': 'ok',
        'reading': {
            'id': latest.id,
            'temperature': latest.temperature,
            'salinity': latest.salinity,
            'ph': latest.ph,
            'dissolved_oxygen': latest.dissolved_oxygen,
            'chlorophyll': latest.chlorophyll,
            'nitrate': latest.nitrate,
            'turbidity': latest.turbidity,
            'latitude': latest.latitude,
            'longitude': latest.longitude,
            'timestamp': latest.timestamp.isoformat(),
        },
    }


@router.get('/history')
def get_sensor_history(db: Session = Depends(get_db)):
    readings = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).all()
    return {'status': 'ok', 'history': [
        {
            'id': reading.id,
            'temperature': reading.temperature,
            'salinity': reading.salinity,
            'ph': reading.ph,
            'dissolved_oxygen': reading.dissolved_oxygen,
            'chlorophyll': reading.chlorophyll,
            'nitrate': reading.nitrate,
            'turbidity': reading.turbidity,
            'latitude': reading.latitude,
            'longitude': reading.longitude,
            'timestamp': reading.timestamp.isoformat(),
        }
        for reading in readings
    ]}
