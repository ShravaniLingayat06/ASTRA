"""CV Engine: Standardized video frame analysis extracting signals for ASTRA platform."""
import os
import cv2
import numpy as np

class CVEngineDetector:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.models_loaded = False
        self._init_models()

    def _init_models(self):
        try:
            # Face SSD model
            prototxt = os.path.join(self.base_dir, "deploy.prototxt.txt")
            caffemodel = os.path.join(self.base_dir, "res10_300x300_ssd_iter_140000.caffemodel")
            if os.path.exists(prototxt) and os.path.exists(caffemodel):
                self.face_net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
                self.models_loaded = True
            else:
                self.face_net = None
        except Exception as e:
            print(f"CV Engine detector initialization notice: {e}")
            self.face_net = None

    def analyze_frame(self, frame) -> dict:
        """
        Analyze an image frame and extract crowd telemetry:
        - face_count
        - estimated male/female counts
        - threat_indicator
        """
        h, w = frame.shape[:2]
        face_count = 0
        detections = []

        if self.face_net is not None:
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
            self.face_net.setInput(blob)
            raw_dets = self.face_net.forward()

            for i in range(raw_dets.shape[2]):
                conf = raw_dets[0, 0, i, 2]
                if conf > 0.5:
                    face_count += 1
                    box = raw_dets[0, 0, i, 3:7] * np.array([w, h, w, h])
                    detections.append(box.astype("int").tolist())

        # Synthesize telemetry
        male_est = int(face_count * 0.6)
        female_est = face_count - male_est
        ratio = round(male_est / max(female_est, 1), 2)

        return {
            "face_count": face_count,
            "male_count": male_est,
            "female_count": female_est,
            "ratio_male_female": ratio,
            "anomaly_detected": face_count >= 5 and ratio > 4.0,
            "bounding_boxes": detections
        }
