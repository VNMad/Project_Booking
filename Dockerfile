FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p logs media static
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps:/app
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#CMD ["python", "manage.py", "migrate"]
#CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["sh", "-c", "sleep 15 && python manage.py makemigrations && python manage.py migrate && (python manage.py createsuperuser --no-input || true) && python manage.py runserver 0.0.0.0:8000"]
