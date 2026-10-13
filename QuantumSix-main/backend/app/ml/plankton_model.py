from __future__ import annotations

import io
import json
from pathlib import Path

import torch
from PIL import Image, UnidentifiedImageError
from torchvision import models

from app.config import settings


class ModelUnavailableError(RuntimeError):
    pass


class PlanktonModel:
    def __init__(self) -> None:
        self.model = None
        self.class_names = [
            'Chaetoceros',
            'Ceratium',
            'Coscinodiscus',
            'Corethron',
            'Ditylum',
            'Gyrodinium',
            'Euglena',
        ]
        self.error = None
        self.model_path = self._resolve_model_path()
        self._load_model()

    def _resolve_model_path(self) -> str | None:
        for candidate in settings.PLANKTON_MODEL_CANDIDATES:
            if not candidate:
                continue
            path = Path(candidate)
            if path.exists():
                return str(path)
        return None

    def is_available(self) -> bool:
        return self.model is not None

    def _load_model(self) -> None:
        model_path = self._resolve_model_path()
        if model_path is None:
            self.error = (
                'Plankton model is not available. Place a trained model at backend/models/best_plankton_model.pth '
                'or set PLANKTON_MODEL_PATH.'
            )
            return

        try:
            checkpoint = torch.load(model_path, map_location='cpu')
            file_class_names = checkpoint.get('class_names') or self.class_names
            self.class_names = file_class_names
            model = models.resnet18(weights=None)
            model.fc = torch.nn.Linear(model.fc.in_features, len(self.class_names))
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()
            self.model = model
            self.model_path = model_path
            self.error = None
        except Exception as exc:  # pragma: no cover - depends on actual model asset
            self.model = None
            self.error = f'Unable to load plankton model: {exc}'

    def predict_image(self, image_bytes: bytes) -> dict:
        if not self.model:
            raise ModelUnavailableError(self.error or 'Plankton model unavailable.')

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        except (OSError, UnidentifiedImageError) as exc:
            raise ValueError('The upload is not a valid image.') from exc

        image = image.resize((224, 224))
        tensor = torch.tensor([[[[0.0]]]])
        # Real PyTorch inference path is used when a model is present.
        with torch.no_grad():
            image_tensor = torch.tensor(list(image.getdata()), dtype=torch.float32).view(224, 224, 3).permute(2, 0, 1).unsqueeze(0)
            image_tensor = image_tensor / 255.0
            image_tensor = (image_tensor - torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)) / torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            logits = self.model(image_tensor)
            probabilities = torch.softmax(logits, dim=1)[0]
            confidence, idx = torch.max(probabilities, dim=0)
            prediction = self.class_names[int(idx.item())]
            return {
                'prediction': prediction,
                'confidence': float(confidence.item()),
                'model': 'plankton_classifier',
            }


plankton_model = PlanktonModel()
