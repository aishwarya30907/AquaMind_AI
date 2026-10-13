from datetime import datetime

from pydantic import BaseModel, Field


class SensorInput(BaseModel):
    temperature: float | None = None
    salinity: float | None = None
    ph: float | None = None
    dissolved_oxygen: float | None = None
    chlorophyll: float | None = None
    nitrate: float | None = None
    turbidity: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: datetime | None = None


class SensorRecord(SensorInput):
    id: int | None = None


class SensorSummary(BaseModel):
    latest: SensorInput | None = None
    history: list[SensorRecord] = Field(default_factory=list)
