# Django Dashboard Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=digestible.settings
ENV PIP_TIMEOUT=300
ENV PIP_RETRIES=5

# Set work directory
WORKDIR /app

# Install system dependencies with faster mirror
RUN sed -i 's/deb.debian.org/deb.debian.org/' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with timeout and retries
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=5 -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash django
RUN chown -R django:django /app
USER django

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "digestible.wsgi:application"]