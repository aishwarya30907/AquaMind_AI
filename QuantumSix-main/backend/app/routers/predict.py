import os
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import services
from app.config import settings
from app.database import get_db
from app.models.records import HABPredictionRecord, PlanktonObservation
from app.schemas.prediction import AnalysisInput, HABFeatureInput, HABPredictionResponse, PlanktonPredictionResponse

router = APIRouter(prefix='/api', tags=['prediction'])
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tif', '.tiff'}


def _normalize_hab_payload(payload: HABFeatureInput | dict) -> dict:
    if isinstance(payload, dict):
        data = payload.copy()
    else:
        data = payload.model_dump(exclude_none=True)
    return {key: float(value) for key, value in data.items() if value is not None and key not in {'latitude', 'longitude', 'timestamp'}}


@router.get('/health')
def health_status() -> dict:
    plankton_status = 'available' if services.plankton_service and services.plankton_service.predict else 'unavailable'
    habitat_status = 'available' if services.hab_service and services.hab_service.predict else 'unavailable'
    return {
        'status': 'ok',
        'service': 'QuantumSix Backend',
        'plankton_model': plankton_status,
        'hab_model': habitat_status,
    }


@router.post('/predict/plankton', response_model=PlanktonPredictionResponse)
async def predict_plankton(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A file is required.')
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsupported file type. Use PNG, JPG, JPEG, BMP, WEBP, TIFF or TIF.')
    if file.content_type and not file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The uploaded file is not an image.')

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The uploaded file is empty.')
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='Uploaded file is too large.')

    try:
        result = services.plankton_service.predict(content)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # if model is missing or cannot load
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc) or 'Plankton model is unavailable.') from exc

    db.add(
        PlanktonObservation(
            prediction=result['prediction'],
            confidence=float(result.get('confidence', 0.0)),
            source='image_upload',
            created_at=datetime.utcnow(),
        )
    )
    db.commit()
    return result


@router.post('/predict/hab', response_model=HABPredictionResponse)
async def predict_hab(payload: HABFeatureInput, db: Session = Depends(get_db)):
    features = payload.model_dump(exclude_none=True)
    try:
        result = services.hab_service.predict(features)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc) or 'HAB model is unavailable.') from exc

    db.add(
        HABPredictionRecord(
            prediction=result['prediction'],
            risk_level=result.get('risk_level', result['prediction']),
            confidence=float(result.get('confidence', 0.0)),
            probabilities=str(result.get('probabilities', {})),
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    )
    db.commit()
    return result


@router.post('/analyze')
async def analyze(payload: AnalysisInput):
    plankton_result = payload.plankton or {}
    hab_result = payload.hab or {}

    if payload.environment and not hab_result:
        try:
            hab_result = services.hab_service.predict(payload.environment.model_dump(exclude_none=True))
        except Exception:
            hab_result = {'prediction': 'Unknown', 'risk_level': 'Unknown', 'confidence': 0.0, 'probabilities': {}}

    if plankton_result:
        plankton_confidence = float(plankton_result.get('confidence', 0.0))
    else:
        plankton_confidence = 0.0

    hab_confidence = float(hab_result.get('confidence', 0.0)) if hab_result else 0.0
    hab_risk = hab_result.get('risk_level', 'Unknown') if hab_result else 'Unknown'

    if hab_risk.lower() in {'high', 'severe'} or plankton_confidence >= 0.75:
        overall_status = 'High alert'
        recommendation = 'Increase sampling frequency and prepare response actions for a likely HAB event.'
    elif hab_risk.lower() in {'medium', 'moderate'} or plankton_confidence >= 0.5:
        overall_status = 'Moderate alert'
        recommendation = 'Continue monitoring and inspect nutrient and plankton conditions in the next cycle.'
    else:
        overall_status = 'Normal'
        recommendation = 'Continue routine monitoring and maintain current sampling schedule.'

    return {
        'plankton': plankton_result,
        'hab': hab_result,
        'overall_status': overall_status,
        'recommendation': recommendation,
    }


@router.post('/predict')
async def legacy_predict(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await predict_plankton(file=file, db=db)
