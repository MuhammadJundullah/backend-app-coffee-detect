# Gunakan base image Python yang lengkap dengan versi 3.10.18
FROM python:3.10.18

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Perbarui daftar paket dan instal dependensi sistem yang diperlukan oleh OpenCV
# Gunakan apt-get clean & rm -rf untuk mengurangi ukuran image
RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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