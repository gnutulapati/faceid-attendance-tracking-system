import os
import requests
import shutil

MODEL_DIR = "models"
URLS = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
}

def reset_and_download():
    # 1. Clean up old corrupted folder
    if os.path.exists(MODEL_DIR):
        print(f"[ACTION] Deleting corrupted '{MODEL_DIR}' folder...")
        shutil.rmtree(MODEL_DIR)
    
    os.makedirs(MODEL_DIR)

    # 2. Download with validation
    for filename, url in URLS.items():
        filepath = os.path.join(MODEL_DIR, filename)
        print(f"[DOWNLOAD] Fetching {filename}...")
        
        try:
            # excessive timeout to handle slow corporate nets
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # 3. VERIFICATION (Crucial Step)
                file_size_kb = os.path.getsize(filepath) / 1024
                print(f"   -> Size: {file_size_kb:.2f} KB")
                
                if file_size_kb < 100:
                    print(f"[ERROR] File is too small! It is likely a text file (firewall block).")
                    os.remove(filepath)
                else:
                    print(f"[SUCCESS] {filename} is valid.")
            else:
                print(f"[ERROR] HTTP {r.status_code} failed.")
        
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")

    print("\n[INSTRUCTION] If the downloads failed above, download these two links manually")
    print("and paste them into the 'models' folder:")
    for name, url in URLS.items():
        print(f" - {name}: {url}")

if __name__ == "__main__":
    reset_and_download()