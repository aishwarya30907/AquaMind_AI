from app.ml.plankton_model import ModelUnavailableError, plankton_model


class PlanktonService:
    def predict(self, image_bytes: bytes) -> dict:
        if not plankton_model.is_available():
            raise ModelUnavailableError(plankton_model.error or 'Plankton model is unavailable.')
        return plankton_model.predict_image(image_bytes)


plankton_service = PlanktonService()
