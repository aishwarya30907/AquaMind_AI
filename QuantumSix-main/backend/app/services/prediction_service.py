import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.records import PredictionRecord


class PredictionService:
    def save_prediction(
        self,
        db: Session,
        prediction_type: str,
        input_metadata: dict | None,
        result: dict,
        confidence: float,
        location: str | None = None,
        user_id: int | None = None,
    ) -> PredictionRecord:
        record = PredictionRecord(
            prediction_type=prediction_type,
            input_metadata=json.dumps(input_metadata or {}, default=str),
            result=json.dumps(result, default=str),
            confidence=float(confidence),
            location=location,
            user_id=user_id,
            timestamp=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_history(self, db: Session) -> list[dict]:
        records = db.query(PredictionRecord).order_by(PredictionRecord.timestamp.desc()).all()
        return [
            {
                'id': record.id,
                'prediction_type': record.prediction_type,
                'input_metadata': json.loads(record.input_metadata) if record.input_metadata else {},
                'result': json.loads(record.result) if record.result else {},
                'confidence': record.confidence,
                'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                'location': record.location,
            }
            for record in records
        ]


prediction_service = PredictionService()
