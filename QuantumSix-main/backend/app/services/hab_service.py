from app.ml.hab_model import ModelUnavailableError, hab_model


class HABService:
    def predict(self, features: dict) -> dict:
        return hab_model.predict(features)


hab_service = HABService()
