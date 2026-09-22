#!/bin/sh

set -e

mkdir -p /app/logs
mkdir -p /app/media
mkdir -p /app/static

touch /app/logs/application_logs.log
touch /app/logs/db_logs.log
touch /app/logs/http_logs.log

echo "=== Waiting for MySQL ==="

until python -c "
import socket
s = socket.socket()
s.settimeout(2)
s.connect(('db', 3306))
s.close()
"; do
    echo "MySQL is not ready. Waiting 2 seconds..."
    sleep 2
done

echo "=== MySQL port is available ==="

python manage.py check --database default

echo "=== Starting Django ==="

exec "$@"