FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create ephemeris directory
RUN mkdir -p /app/ephe

EXPOSE 8000

# Use PORT from environment (Render sets this)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
