import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent


def _split_env(value: str, default: str) -> list[str]:
    if not value:
        return [item.strip() for item in default.split(',') if item.strip()]
    return [item.strip() for item in value.split(',') if item.strip()]


class Settings:
    APP_NAME = os.getenv('APP_NAME', 'QuantumSix Backend')
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "app.db"}')
    JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-development')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    ALLOWED_ORIGINS = _split_env(os.getenv('ALLOWED_ORIGINS', ''), os.getenv('FRONTEND_URL', 'http://localhost:5173'))
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '5242880'))
    MODEL_PATH = os.getenv('MODEL_PATH', '')
    PLANKTON_MODEL_CANDIDATES = [
        os.getenv('PLANKTON_MODEL_PATH', ''),
        str(BASE_DIR / 'models' / 'best_plankton_model.pth'),
        str(PROJECT_ROOT / 'models' / 'best_plankton_model.pth'),
        str(PROJECT_ROOT / 'AquaMind' / 'models' / 'best_plankton_model.pth'),
    ]
    HAB_MODEL_CANDIDATES = [
        os.getenv('HAB_MODEL_PATH', ''),
        str(BASE_DIR / 'models' / 'hab_model.joblib'),
        str(PROJECT_ROOT / 'models' / 'hab_model.joblib'),
    ]
    UPLOAD_DIR = BASE_DIR / 'uploads'
    API_PREFIX = '/api'


settings = Settings()
