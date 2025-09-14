# Gunakan base image Python yang ringan
FROM python:3.11-slim

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
COPY requirements.txt .

# Instal dependensi yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek Anda ke direktori kerja
COPY . .

# Paparkan port yang digunakan aplikasi
EXPOSE 8000

# Perintah untuk menjalankan aplikasi
# Ganti 'main' dengan nama file Python Anda dan 'app' dengan instance 
# FastAPI Anda
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
