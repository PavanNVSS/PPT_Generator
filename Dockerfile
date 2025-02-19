# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt # FOR PRODUCTION ONLY
RUN pip install -r requirements.txt
# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8601 to the outside world
EXPOSE 8601

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8601", "--server.address", "0.0.0.0"]
