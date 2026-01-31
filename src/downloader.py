import os
import requests

MODEL_DIR = "models"
URLS = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
}

def get_models():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    for filename, url in URLS.items():
        filepath = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[INFO] Downloading {filename}...")
            r = requests.get(url)
            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"[SUCCESS] Downloaded {filename}")
        else:
            print(f"[INFO] {filename} ready.")

if __name__ == "__main__":
    get_models()