# Gunakan base image Miniconda
FROM continuumio/miniconda3:latest

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file environment.yml ke direktori kerja
COPY environment.yml .

# Buat lingkungan Conda dari file environment.yml
RUN conda env create -f environment.yml

# Atur lingkungan Conda agar aktif secara default saat masuk ke shell
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Salin semua file proyek Anda ke direktori kerja
COPY . .

# Paparkan port yang digunakan aplikasi
EXPOSE 8000

# Perintah untuk menjalankan aplikasi
CMD ["conda", "run", "-n", "myenv", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]