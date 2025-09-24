# Stage 1: Build environment
FROM continuumio/miniconda3:latest AS builder

WORKDIR /app

# Copy environment file first (for better caching)
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy  # ← CLEAN CACHE!

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Production image
FROM continuumio/miniconda3:latest

WORKDIR /app

# Copy only conda environment from builder
COPY --from=builder /opt/conda/envs/fastapi_yolo_env /opt/conda/envs/fastapi_yolo_env

# Copy system dependencies if needed
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# Install minimal system dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Use conda run more efficiently
ENV PATH /opt/conda/envs/fastapi_yolo_env/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]