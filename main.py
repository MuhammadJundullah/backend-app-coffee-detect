import io
import cv2
import uvicorn
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from ultralytics import YOLO

# Inisialisasi FastAPI
app = FastAPI()

# Memuat model YOLOv8
model = YOLO('weight/yolov8n.pt')

# Endpoint untuk deteksi gambar
@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """
    Menerima upload gambar dan mengembalikan gambar dengan deteksi objek.
    """
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # Melakukan inferensi pada gambar
    results = model(image)
    
    # Menggambar hasil pada gambar
    result_image = results[0].plot()
    result_image = Image.fromarray(result_image[..., ::-1])
    
    # Menyimpan gambar hasil ke buffer dan mengembalikannya
    img_byte_arr = io.BytesIO()
    result_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/jpeg")

# Endpoint untuk deteksi video
@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...)):
    """
    Menerima upload video, memproses setiap frame, dan mengembalikan video baru.
    """
    # Kode ini akan lebih kompleks dan biasanya memerlukan
    # menyimpan file sementara dan memprosesnya secara frame-by-frame
    # menggunakan OpenCV. Ini adalah contoh yang lebih sederhana.
    # Untuk kasus nyata, pertimbangkan memproses secara asinkronus
    # dan mengembalikan URL ke video hasil.
    return {"message": "Endpoint untuk video sedang dalam pengembangan."}

# Endpoint untuk deteksi real-time (streaming dari webcam)
# Endpoint ini akan memerlukan pendekatan yang berbeda, biasanya
# menggunakan WebSocket atau streaming HTTP.
@app.get("/stream/realtime")
async def realtime_stream():
    """
    Streaming video real-time dengan deteksi objek dari kamera.
    """
    def generate_frames():
        camera = cv2.VideoCapture(1)  # Ganti dengan URL stream jika perlu
        if not camera.isOpened():
            return
        
        while True:
            success, frame = camera.read()
            if not success:
                break
            
            # Lakukan inferensi pada frame
            results = model(frame, verbose=False)
            
            # Gambar kotak hasil pada frame
            annotated_frame = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
        camera.release()
        
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

# Untuk menjalankan server:
# uvicorn main:app --reload