#!/bin/bash

set -e

cd /opt/Project_Booking

echo "======================================"
echo "1. Pulling project from GitHub"
echo "======================================"

git pull --ff-only


echo "======================================"
echo "2. Building Docker image"
echo "======================================"

docker compose build


echo "======================================"
echo "3. Starting MySQL"
echo "======================================"

docker compose up -d db


echo "======================================"
echo "4. Waiting for MySQL"
echo "======================================"

until [ "$(docker inspect -f '{{.State.Health.Status}}' booking_db 2>/dev/null)" = "healthy" ]; do
    echo "MySQL is not ready. Waiting..."
    sleep 2
done

echo "MySQL is healthy."


echo "======================================"
echo "5. Django check"
echo "======================================"

docker compose run --rm web \
    python manage.py check --database default


echo "======================================"
echo "6. Creating migrations"
echo "======================================"

echo "--- Users ---"
docker compose run --rm web \
    python manage.py makemigrations users

echo "--- Listings ---"
docker compose run --rm web \
    python manage.py makemigrations listings

echo "--- Bookings ---"
docker compose run --rm web \
    python manage.py makemigrations bookings

echo "--- Reviews ---"
docker compose run --rm web \
    python manage.py makemigrations reviews

echo "--- Statistic ---"
docker compose run --rm web \
    python manage.py makemigrations statistic

echo "--- Final migration check ---"
docker compose run --rm web \
    python manage.py makemigrations


echo "======================================"
echo "7. Applying user migrations"
echo "======================================"

docker compose run --rm web \
    python manage.py migrate users


echo "======================================"
echo "8. Applying all migrations"
echo "======================================"

docker compose run --rm web \
    python manage.py migrate


echo "======================================"
echo "9. Collecting static files"
echo "======================================"

docker compose run --rm web \
    python manage.py collectstatic --noinput


echo "======================================"
echo "10. Creating superuser"
echo "======================================"

docker compose run --rm web \
    python manage.py createsuperuser --noinput || true


echo "======================================"
echo "11. Starting Django"
echo "======================================"

docker compose up -d


echo "======================================"
echo "12. Removing unused Docker images"
echo "======================================"

docker image prune -f


echo "======================================"
echo "Deployment finished"
echo "======================================"

docker compose ps