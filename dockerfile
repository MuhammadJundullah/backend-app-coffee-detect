# Gunakan base image resmi dari Continuum Analytics yang sudah menyertakan OpenCV dan dependensinya
FROM continuumio/miniconda3:latest

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
COPY requirements.txt .

# Instal dependensi Python yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek Anda ke direktori kerja
COPY . .

# Paparkan port yang digunakan aplikasi
EXPOSE 8000

# Perintah untuk menjalankan aplikasi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]