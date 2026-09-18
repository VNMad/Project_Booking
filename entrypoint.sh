#!/bin/bash
set -e

echo "=== 1. Ожидание готовности MySQL ==="
until python -c "
import sys, os, MySQLdb
try:
    MySQLdb.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'user_connect'),
        passwd=os.environ.get('MYSQL_PASSWORD', 'your_password'),
        db=os.environ.get('MYSQL_DATABASE', 'booking_db'),
        port=int(os.environ.get('MYSQL_PORT', 3306))
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "MySQL еще инициализируется, ждем 2 сек..."
  sleep 2
done

echo "MySQL готов к работе!"

echo "=== 2. Генерация файлов миграций ==="
python manage.py makemigrations users
python manage.py makemigrations listings
python manage.py makemigrations bookings
python manage.py makemigrations reviews
python manage.py makemigrations statistic
python manage.py makemigrations

echo "=== 3. Первичный запуск миграций (Строго сначала Users!) ==="
# Принудительно создаем таблицу кастомного пользователя первее системного admin
python manage.py migrate users
python manage.py migrate

echo "=== 4. Сборка статики ==="
python manage.py collectstatic --no-input || true

echo "=== 5. Создание суперпользователя ==="
python manage.py createsuperuser --no-input || true

echo "=== 6. Запуск Django ==="
exec "$@"