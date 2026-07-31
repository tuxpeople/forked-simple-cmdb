FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Set environment variable to indicate Docker container
ENV DOCKER_CONTAINER=1

# Inside the container the app must bind all interfaces so the published
# port works; debug stays off because FLASK_DEBUG is unset (RISK-102)
ENV CMDB_HOST=0.0.0.0

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]