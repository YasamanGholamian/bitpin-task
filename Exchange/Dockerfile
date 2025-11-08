# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirement.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirement.txt

# Copy the entire Exchange project
COPY Exchange /app/Exchange

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=Exchange.settings
ENV PYTHONPATH=/app

# Collect static files
RUN python3 /app/Exchange/manage.py collectstatic --noinput

# Expose the port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "Exchange.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

