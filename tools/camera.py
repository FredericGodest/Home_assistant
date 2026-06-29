import os
import cv2
import logging
from datetime import datetime
from ultralytics import YOLO
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

MODEL = YOLO("yolov8n.pt")

def build_rtsp_url(user: str, password: str, ip: str) -> str:
    return f"rtsp://{user}:{password}@{ip}/stream1"

@tool
def capture_and_detect() -> dict:
    """
    Capture une frame depuis la caméra Tapo, 
    applique YOLOv8 et sauvegarde le résultat horodaté.
    """
    RTSP_URL = build_rtsp_url(
        user=os.getenv("TAPO_USER", "admin"),
        password=os.getenv("TAPO_PASSWORD"),
        ip=os.getenv("TAPO_IP"),
    )

    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        raise ConnectionError("Impossible de se connecter à la caméra")

    try:
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Frame non capturée")

        results = MODEL(frame)
        annotated = results[0].plot()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"frame_detected_{timestamp}.jpg"
        save_path = os.path.join(r"frames", image_name)
        cv2.imwrite(str(save_path), annotated)

        detections = [
            {"label": MODEL.names[int(b.cls)], "confidence": round(float(b.conf), 2)}
            for b in results[0].boxes
        ]

        logger.info(f"✅ Sauvegardé : {save_path} — {len(detections)} objet(s)")
        return {"saved_to": str(save_path), "detections": detections}

    finally:
        cap.release()

