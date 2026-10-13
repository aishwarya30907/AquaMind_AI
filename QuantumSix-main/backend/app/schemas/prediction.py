from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class HABFeatureInput(BaseModel):
    model_config = ConfigDict(extra='allow')

    temperature: float | None = None
    salinity: float | None = None
    ph: float | None = None
    dissolved_oxygen: float | None = None
    chlorophyll: float | None = None
    nitrate: float | None = None
    ammonia: float | None = None
    turbidity: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: datetime | None = None


class PlanktonPredictionResponse(BaseModel):
    prediction: str
    confidence: float
    model: str = 'plankton_classifier'


class HABPredictionResponse(BaseModel):
    prediction: str
    risk_level: str
    confidence: float
    probabilities: dict[str, float] = Field(default_factory=dict)
    model: str = 'hab_predictor'


class AnalysisInput(BaseModel):
    plankton: dict | None = None
    hab: dict | None = None
    environment: HABFeatureInput | None = None


class AnalysisResponse(BaseModel):
    plankton: dict | None = None
    hab: dict | None = None
    overall_status: str
    recommendation: str
