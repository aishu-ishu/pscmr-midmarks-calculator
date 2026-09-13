FROM python:3.10-slim

# Install modern system dependencies required for OpenCV and EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run Gunicorn with 1 worker to stay within memory limits
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 120 app:app
