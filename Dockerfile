FROM python:3.10-slim

# Install system libraries needed by OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Start app using 1 worker to save memory
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 120 app:app
