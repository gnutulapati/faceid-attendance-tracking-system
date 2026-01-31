import cv2
import numpy as np
import os
import pickle
from src.downloader import get_models

# Paths
MODEL_DIR = "models"
DB_PATH = os.path.join("data", "encodings.pkl")
DETECTOR_PATH = os.path.join(MODEL_DIR, "face_detection_yunet_2023mar.onnx")
RECOGNIZER_PATH = os.path.join(MODEL_DIR, "face_recognition_sface_2021dec.onnx")

class FaceSystem:
    def __init__(self):
        # 1. Ensure models are present
        get_models()
        
        # 2. Load Models
        # YuNet: (Input Size: 320x320, Conf Threshold: 0.9, NMS: 0.3, TopK: 5000)
        self.detector = cv2.FaceDetectorYN.create(DETECTOR_PATH, "", (320, 320), 0.9, 0.3, 5000)
        self.recognizer = cv2.FaceRecognizerSF.create(RECOGNIZER_PATH, "")
        
        # 3. Load Database
        self.db = {"names": [], "encodings": []}
        self.load_db()

    def load_db(self):
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as f:
                self.db = pickle.load(f)

    def save_db(self):
        with open(DB_PATH, "wb") as f:
            pickle.dump(self.db, f)

    def process_image(self, img_bgr):
        # YuNet needs the input size set every time if image size changes
        h, w, _ = img_bgr.shape
        self.detector.setInputSize((w, h))
        
        # Detect
        faces = self.detector.detect(img_bgr)
        
        # faces[1] contains the list of bounding boxes
        if faces[1] is None:
            return None, None
            
        # Get the first face (highest confidence)
        face_data = faces[1][0]
        
        # Align and Crop using SFace
        aligned_face = self.recognizer.alignCrop(img_bgr, face_data)
        
        # Generate Embedding (Feature Vector)
        feature = self.recognizer.feature(aligned_face)
        
        return face_data, feature

    def register_user(self, img_bgr, name):
        _, feature = self.process_image(img_bgr)
        if feature is None:
            return False, "No face detected"
            
        self.db["names"].append(name)
        self.db["encodings"].append(feature)
        self.save_db()
        return True, f"Registered {name}"

    def identify(self, img_bgr):
        _, feature = self.process_image(img_bgr)
        if feature is None:
            return "No Face", 0.0

        if not self.db["encodings"]:
            return "Unknown", 0.0

        max_score = 0.0
        best_match = "Unknown"
        
        # SFace uses Cosine Similarity. 
        # Standard threshold is roughly 0.363. Higher is better.
        # We use 0.4 for higher strictness.
        THRESHOLD = 0.4
        
        for name, db_enc in zip(self.db["names"], self.db["encodings"]):
            score = self.recognizer.match(feature, db_enc, cv2.FaceRecognizerSF_FR_COSINE)
            if score > max_score:
                max_score = score
                if score > THRESHOLD:
                    best_match = name
                    
        return best_match, max_score