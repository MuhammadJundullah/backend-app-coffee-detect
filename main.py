from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import uvicorn
import cv2
import io
import numpy as np
from PIL import Image

# Inisialisasi FastAPI
app = FastAPI()

# Konfigurasi CORS Middleware
# Penting untuk mengatasi masalah 400 Bad Request
# Origins harus mencakup URL frontend Anda
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Memungkinkan semua metode HTTP, termasuk OPTIONS
    allow_headers=["*"],  # Memungkinkan semua header
)

# Memuat model YOLOv8
# Pastikan jalur ke bobot model sudah benar
try:
    model = YOLO('weight/yolov8n.pt')
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

# Endpoint untuk deteksi gambar (menerima upload)
@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """
    Menerima upload gambar dan mengembalikan gambar dengan deteksi objek.
    """
    if not model:
        return {"error": "YOLO model tidak berhasil dimuat."}, 500
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        results = model(image, conf=0.1)
        result_image = results[0].plot(labels=True, conf=True, boxes=True, font_size=10, line_width=5)
        # result_image = results[0].plot()
        result_image = Image.fromarray(result_image[..., ::-1])
        img_byte_arr = io.BytesIO()
        result_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")
    except Exception as e:
        return {"error": f"Terjadi kesalahan saat memproses gambar: {e}"}

# Endpoint untuk deteksi video (menerima upload)
@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...)):
    """
    Menerima upload video, memproses setiap frame, dan mengembalikan video baru.
    """
    if not model:
        return {"error": "YOLO model tidak berhasil dimuat."}, 500
    try:
        video_path = f"/tmp/{file.filename}"
        with open(video_path, "wb") as buffer:
            buffer.write(await file.read())

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "Tidak dapat membuka file video."}

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = f"/tmp/output_{file.filename}"
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        cap.release()
        out.release()

        with open(output_path, "rb") as video_file:
            video_bytes = video_file.read()

        return StreamingResponse(io.BytesIO(video_bytes), media_type="video/mp4")
    
    except Exception as e:
        return {"error": f"Terjadi kesalahan saat memproses video: {e}"}

# Endpoint untuk deteksi real-time (streaming dari webcam)
@app.get("/stream/realtime")
async def realtime_stream():
    """
    Streaming video real-time dengan deteksi objek dari kamera.
    """
    if not model:
        return {"error": "YOLO model tidak berhasil dimuat."}, 500
    
    def generate_frames():
        camera = cv2.VideoCapture(1)
        if not camera.isOpened():
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'{"error": "Kamera tidak dapat diakses."}' + b'\r\n')
            return
        
        while True:
            success, frame = camera.read()
            if not success:
                break
            
            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
        camera.release()
        
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

# Endpoint baru menggunakan WebSocket
@app.websocket("/ws/stream/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """
    Streaming video real-time dengan deteksi objek dari kamera melalui WebSocket.
    """
    await websocket.accept()
    if not model:
        await websocket.send_json({"error": "YOLO model tidak berhasil dimuat."})
        await websocket.close()
        return

    cap = cv2.VideoCapture(1)  # Ganti dengan 1 jika webcam default tidak berfungsi
    if not cap.isOpened():
        await websocket.send_json({"error": "Kamera tidak dapat diakses."})
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Lakukan deteksi objek
            results = model(frame, verbose=False, conf=0.8)
            annotated_frame = results[0].plot()

            # Encode frame yang sudah diannotasi menjadi JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if ret:
                # Kirim frame sebagai byte melalui WebSocket
                await websocket.send_bytes(buffer.tobytes())
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        cap.release()
        await websocket.close()

# Endpoint OPTIONS eksplisit untuk semua jalur
@app.options("/{path:path}")
async def preflight_handler(path: str):
    return Response(status_code=200)




