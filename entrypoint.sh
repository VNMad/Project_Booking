#!/bin/bash
set -e

mkdir -p /app/logs
touch /app/logs/application_logs.log
touch /app/logs/db_logs.log
touch /app/logs/http_logs.log

echo "=== 1. Ожидание готовности MySQL (Порт 3306) ==="
# Ждем физической готовности сетевого порта MySQL
until python -c "import socket; s = socket.socket(); s.settimeout(2); s.connect(('db', 3306)); s.close()"; do
  echo "MySQL порт 3306 еще не доступен, ждем 2 сек..."
  sleep 2
done

echo "Порт БД открыт! Проверяем авторизацию Django..."

# Показываем реальную ошибку, если Django не может подключиться к БД
python manage.py check --database default

echo "=== MySQL и Django успешно связались! ==="

echo "=== 2. Генерация файлов миграций ==="
python manage.py makemigrations users
python manage.py makemigrations listings
python manage.py makemigrations bookings
python manage.py makemigrations reviews
python manage.py makemigrations statistic
python manage.py makemigrations

echo "=== 3. Первичный запуск миграций (Строго сначала Users!) ==="
# Сначала создаем таблицу пользователей, чтобы системный admin не упал с ошибкой
python manage.py migrate users
python manage.py migrate

echo "=== 4. Сборка статики ==="
python manage.py collectstatic --no-input || true

echo "=== 5. Создание суперпользователя ==="
python manage.py createsuperuser --no-input || true

echo "=== 6. Запуск Django ==="
exec "$@"
