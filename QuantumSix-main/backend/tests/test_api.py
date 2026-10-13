import os
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

os.environ['DATABASE_URL'] = 'sqlite:///./test_app.db'

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    from app.database import engine

    with engine.begin() as conn:
        conn.exec_driver_sql('DELETE FROM users')
        conn.exec_driver_sql('DELETE FROM prediction_records')
        conn.exec_driver_sql('DELETE FROM plankton_observations')
        conn.exec_driver_sql('DELETE FROM hab_prediction_records')
        conn.exec_driver_sql('DELETE FROM sensor_readings')
        conn.exec_driver_sql('DELETE FROM location_observations')
    yield


def test_health_endpoint():
    response = client.get('/api/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] in {'ok', 'degraded'}
    assert payload['service'] == 'QuantumSix Backend'


def test_register_and_login():
    username = 'demouser'
    password = 'SecurePass123!'

    response = client.post('/api/auth/register', json={'username': username, 'password': password})
    assert response.status_code == 200
    data = response.json()
    assert data['user']['username'] == username
    assert 'access_token' in data

    login = client.post('/api/auth/login', json={'username': username, 'password': password})
    assert login.status_code == 200
    assert login.json()['user']['username'] == username


def test_plankton_prediction_requires_image():
    response = client.post('/api/predict/plankton')
    assert response.status_code == 422


def test_plankton_prediction_with_mocked_model(monkeypatch):
    from app import services as services_module

    class MockPlanktonModel:
        def predict_image(self, image_bytes):
            return {'prediction': 'Chaetoceros', 'confidence': 0.98, 'model': 'plankton_classifier'}

    monkeypatch.setattr(services_module, 'plankton_service', type('S', (), {'predict': lambda self, image_bytes: {'prediction': 'Chaetoceros', 'confidence': 0.98, 'model': 'plankton_classifier'}})())

    image = BytesIO(b'fake-image')
    response = client.post('/api/predict/plankton', files={'file': ('sample.png', image.getvalue(), 'image/png')})
    assert response.status_code == 200
    payload = response.json()
    assert payload['prediction'] == 'Chaetoceros'
    assert payload['confidence'] >= 0


def test_hab_prediction_accepts_features():
    payload = {
        'temperature': 28.0,
        'salinity': 32.0,
        'ph': 7.5,
        'dissolved_oxygen': 7.2,
        'chlorophyll': 15.0,
        'nitrate': 2.0,
    }
    response = client.post('/api/predict/hab', json=payload)
    assert response.status_code == 200
    result = response.json()
    assert 'prediction' in result
    assert 'risk_level' in result
    assert 'confidence' in result


def test_invalid_input_returns_400():
    response = client.post('/api/predict/hab', json={'temperature': 'hot'})
    assert response.status_code == 422
