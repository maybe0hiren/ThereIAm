import cv2
from pathlib import Path
from typing import List, Tuple

MODEL_PATH = Path(__file__).parent / "face_detection_yunet_2023mar.onnx"
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "YuNet model not found. "
        "Place 'face_detection_yunet_2023mar.onnx' next to face_detector.py"
    )
Vertex = Tuple[int, int]
FaceVertices = List[Vertex]
_detector = None
def _get_detector(w: int, h: int):
    global _detector
    if _detector is None:
        _detector = cv2.FaceDetectorYN.create(
            model=str(MODEL_PATH),
            config="",
            input_size=(w, h),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=5000
        )
    else:
        _detector.setInputSize((w, h))
    return _detector

def detectFaces(image) -> List[FaceVertices]:
    if image is None:
        raise ValueError("Image is None")
    h, w = image.shape[:2]
    detector = _get_detector(w, h)
    _, faces = detector.detect(image)
    faceVertices: List[FaceVertices] = []
    if faces is not None:
        for face in faces:
            x, y, fw, fh = map(int, face[:4])
            faceVertices.append([
                (x, y),
                (x + fw, y),
                (x + fw, y + fh),
                (x, y + fh)
            ])
    return faceVertices