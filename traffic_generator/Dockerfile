# Use a lightweight, official Python image to keep the container footprint small
FROM python:3.11-slim

# Prevent Python from writing pyc files and keep stdout/stderr unbuffered for logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install necessary system dependencies (e.g., for compiling certain cryptography libs if needed by asyncssh)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual asynchronous generation script into the container
COPY generator.py .

# Create a non-root user for security best practices (Platform Engineering standard)
RUN useradd -m generator_user
USER generator_user

# Execute the baseline traffic script
CMD ["python", "generator.py"]