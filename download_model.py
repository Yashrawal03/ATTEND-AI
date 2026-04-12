import urllib.request
import os
import ssl

# Fix SSL certificate issues on Windows
ssl._create_default_https_context = ssl._create_unverified_context

os.makedirs("static/models", exist_ok=True)

# Correct URLs from unpkg.com
files = {
    "tiny_face_detector_model-shard1":
        "https://unpkg.com/face-api.js@0.22.2/weights/tiny_face_detector_model-shard1",
    "tiny_face_detector_model-weights_manifest.json":
        "https://unpkg.com/face-api.js@0.22.2/weights/tiny_face_detector_model-weights_manifest.json",
    "face_landmark_68_model-shard1":
        "https://unpkg.com/face-api.js@0.22.2/weights/face_landmark_68_model-shard1",
    "face_landmark_68_model-weights_manifest.json":
        "https://unpkg.com/face-api.js@0.22.2/weights/face_landmark_68_model-weights_manifest.json",
    "face_recognition_model-shard1":
        "https://unpkg.com/face-api.js@0.22.2/weights/face_recognition_model-shard1",
    "face_recognition_model-weights_manifest.json":
        "https://unpkg.com/face-api.js@0.22.2/weights/face_recognition_model-weights_manifest.json",
}

print("Starting download...\n")

for filename, url in files.items():
    path = f"static/models/{filename}"
    print(f"Downloading {filename}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, path)
        size = os.path.getsize(path)
        ok = "OK" if size > 1000 else "FAILED - too small"
        print(f"{size:,} bytes  [{ok}]")
    except Exception as e:
        print(f"ERROR: {e}")

print("\n--- Final check ---")
expected = {
    "tiny_face_detector_model-shard1": 180000,
    "face_landmark_68_model-shard1": 300000,
    "face_recognition_model-shard1": 6000000,
}
all_ok = True
for filename, min_size in expected.items():
    path = f"static/models/{filename}"
    size = os.path.getsize(path) if os.path.exists(path) else 0
    ok = size >= min_size
    if not ok:
        all_ok = False
    print(f"  {'✓' if ok else '✗'} {filename}: {size:,} bytes")

if all_ok:
    print("\n✓ All models downloaded correctly! Run: python app.py")
else:
    print("\n✗ Some files are too small. Check your internet connection.")