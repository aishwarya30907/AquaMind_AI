from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, init_db
from app.routers.auth import router as auth_router
from app.routers.locations import router as locations_router
from app.routers.predict import router as predict_router
from app.routers.predictions import router as predictions_router
from app.routers.sensors import router as sensors_router

app = FastAPI(
    title='QuantumSix Backend',
    version='1.0.0',
    description='AI-powered HAB monitoring and plankton classification backend for QuantumSix.',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup_event() -> None:
    init_db()


init_db()


@app.get('/api/health')
def health_check() -> dict:
    return {
        'status': 'ok',
        'service': 'QuantumSix Backend',
        'database': 'sqlite',
    }


@app.get('/health')
def legacy_health_check() -> dict:
    return {'status': 'ok', 'service': 'QuantumSix Backend'}


app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(predictions_router)
app.include_router(sensors_router)
app.include_router(locations_router)
