# Mandatory AMD ROCm Base Image
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies without clobbering ROCm torch
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Explicitly verify PyTorch is still the official ROCm build
RUN python3 -c "import torch; assert '+rocm' in torch.__version__, f'Fatal: PyTorch overwritten by non-ROCm version: {torch.__version__}'; print('ROCm PyTorch Verified:', torch.__version__)"

# Copy pre-baked model weights to /models and /app/models per AMD specification
COPY models /models
COPY models /app/models

# Pre-populate ~/.EasyOCR/model for seamless offline execution
RUN mkdir -p /root/.EasyOCR/model && cp /models/* /root/.EasyOCR/model/

# Copy application source code and parsers
COPY parsers /app/parsers
COPY indexer.py /app/indexer.py
COPY engine.py /app/engine.py
COPY app.py /app/app.py

# Ensure standard evaluation directories exist
RUN mkdir -p /app/corpus /app/output /app/index_cache

# Default command
CMD ["python3", "/app/app.py", "--help"]
