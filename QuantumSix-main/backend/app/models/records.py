from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)


class PredictionRecord(Base):
    __tablename__ = 'prediction_records'

    id = Column(Integer, primary_key=True, index=True)
    prediction_type = Column(String(50), index=True, nullable=False)
    input_metadata = Column(Text, nullable=True)
    result = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)


class PlanktonObservation(Base):
    __tablename__ = 'plankton_observations'

    id = Column(Integer, primary_key=True, index=True)
    prediction = Column(String(100), nullable=False)
    confidence = Column(Float, default=0.0)
    source = Column(String(50), default='image_upload')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(200), nullable=True)


class HABPredictionRecord(Base):
    __tablename__ = 'hab_prediction_records'

    id = Column(Integer, primary_key=True, index=True)
    prediction = Column(String(100), nullable=False)
    risk_level = Column(String(50), nullable=False)
    confidence = Column(Float, default=0.0)
    probabilities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


class SensorReading(Base):
    __tablename__ = 'sensor_readings'

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    salinity = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    dissolved_oxygen = Column(Float, nullable=True)
    chlorophyll = Column(Float, nullable=True)
    nitrate = Column(Float, nullable=True)
    turbidity = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class LocationObservation(Base):
    __tablename__ = 'location_observations'

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    hab_risk = Column(String(50), nullable=True)
    plankton_observation = Column(String(200), nullable=True)
    sensor_observation = Column(Text, nullable=True)
