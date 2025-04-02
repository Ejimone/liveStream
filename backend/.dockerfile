# Stage 1: Build stage (optional, if you have build steps)
# FROM python:3.11-slim as builder
# WORKDIR /app
# COPY requirements.txt .
# RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies (like postgresql-client if needed for backups/checks)
# RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy built wheels from builder stage (if used)
# COPY --from=builder /wheels /wheels
# COPY --from=builder /app/requirements.txt .
# RUN pip install --no-cache /wheels/*

# Install dependencies directly if not using multi-stage wheel build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Create user for running the application (optional but good practice)
# RUN addgroup --system app && adduser --system --group app
# USER app

# Collect static files (if Django serves static files directly, not recommended for production)
# RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Gunicorn
# Adjust workers based on your server resources
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "classroom_copilot_project.wsgi:application"]

# Command to run Celery worker (Use this in a separate container/service)
# CMD ["celery", "-A", "classroom_copilot_project", "worker", "--loglevel=info"]

# Command to run Celery beat (Use this in a separate container/service)
# CMD ["celery", "-A", "classroom_copilot_project", "beat", "--loglevel=info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]