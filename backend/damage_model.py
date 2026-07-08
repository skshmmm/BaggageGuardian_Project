# backend/damage_model.py
from ultralytics import YOLO
from functools import lru_cache

MODEL_PATH = "weights/baggage_damage.pt"  # <-- your trained YOLOv8 weights


@lru_cache(maxsize=1)
def get_yolo_model():
    """
    Load YOLO model once at startup and reuse.
    """
    model = YOLO(MODEL_PATH)
    return model
