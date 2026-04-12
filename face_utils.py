import os
import shutil

FACE_DATA_DIR = "face_data"

def get_student_photo_list():
    """Return all photos from face_data/ for face recognition loading."""
    result = []
    if not os.path.exists(FACE_DATA_DIR):
        os.makedirs(FACE_DATA_DIR)
        return result
    for folder in os.listdir(FACE_DATA_DIR):
        folder_path = os.path.join(FACE_DATA_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        parts = folder.split("_", 1)
        student_id = parts[0]
        name = parts[1].replace("_", " ") if len(parts) > 1 else student_id
        for f in os.listdir(folder_path):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                result.append({
                    "student_id": student_id,
                    "name": name,
                    "photo_url": f"/api/photo/{folder}/{f}"
                })
                break  # one photo per student for loading
    return result

def delete_student_photos(student_id):
    if not os.path.exists(FACE_DATA_DIR):
        return
    for folder in os.listdir(FACE_DATA_DIR):
        if folder.startswith(f"{student_id}_"):
            shutil.rmtree(os.path.join(FACE_DATA_DIR, folder), ignore_errors=True)