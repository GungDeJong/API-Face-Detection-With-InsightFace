from fastapi import FastAPI, UploadFile, File
import numpy as np
from PIL import Image, ImageDraw
import io
import base64
import insightface

app = FastAPI()

# Inisialisasi Model InsightFace
detector = insightface.model_zoo.get_model('det_10g.onnx')
detector.prepare(ctx_id=0, input_size=(640, 640))

def draw_with_pillow(img, faces):
    """Gambar bounding box menggunakan Pillow."""
    img_pillow = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pillow)
    for face in faces:
        x1, y1, x2, y2 = face[:4].astype(int)
        draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=3)  # Warna merah (RGB)
    return np.array(img_pillow)

def encode_image_to_base64(image):
    """Encode gambar ke base64."""
    img_pillow = Image.fromarray(image)
    buffered = io.BytesIO()
    img_pillow.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.post("/detect_faces/")
async def detect_faces(file: UploadFile = File(...)):
    # Membaca file gambar
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)

    # Debug format warna awal
    print("Image original format:", image.shape)

    # Deteksi wajah
    bboxes, _ = detector.detect(image)

    # Terapkan threshold
    threshold = 0.5
    filtered_bboxes = [bbox for bbox in bboxes if bbox[4] > threshold]

    # Gambar bounding box menggunakan Pillow
    image_with_boxes = draw_with_pillow(image, filtered_bboxes)

    # Debug format warna setelah bounding box
    print("Image after drawing bounding boxes:", image_with_boxes.shape)

    # Encode gambar ke base64
    base64_image = encode_image_to_base64(image_with_boxes)

    return {
        "status": "success",
        "face_count": len(filtered_bboxes),
        "base64_image": base64_image
    }