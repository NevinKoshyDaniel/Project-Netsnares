# Use a lightweight, official Python image to keep the container footprint small
FROM python:3.11-slim

# Prevent Python from writing pyc files and keep stdout/stderr unbuffered for logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generator.py .

RUN useradd -m generator_user
USER generator_user

# Execute the baseline traffic script
CMD ["python", "generator.py"]