# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TESSERACT_CMD=/usr/bin/tesseract

# Install system dependencies (Tesseract, Poppler for PDF, C++ for hnswlib)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ara \
    libtesseract-dev \
    poppler-utils \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (required for HuggingFace Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Install Python dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY --chown=user . .

# Create writable directories for uploads and data
RUN mkdir -p $HOME/app/data/uploads $HOME/app/data/chroma_db $HOME/app/logs

# Create startup script
RUN echo '#!/bin/bash\n\
    uvicorn api.main:app --host 0.0.0.0 --port 8000 &\n\
    streamlit run interface/app.py --server.port 7860 --server.address 0.0.0.0\n\
    wait -n\n\
    exit $?' > $HOME/app/start.sh && chmod +x $HOME/app/start.sh

# Expose port (7860 is standard for Hugging Face Spaces)
EXPOSE 7860

# Run the startup script
CMD ["./start.sh"]
