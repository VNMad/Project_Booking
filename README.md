# Project Booking
# Проект Booking

Backend API for an accommodation rental and booking service.
Backend API для сервиса аренды жилья и бронирования.

The project is built with Django and Django REST Framework.
Проект разработан на Django и Django REST Framework.

---

## Features
## Возможности

- User registration and JWT authentication.
- Регистрация пользователей и JWT-аутентификация.

- Apartment listing management.
- Управление объявлениями об аренде квартир.

- Search, filtering, sorting and pagination.
- Поиск, фильтрация, сортировка и пагинация.

- Listing photo management.
- Управление фотографиями объявлений.

- Soft deletion and restoration of listings.
- Мягкое удаление и восстановление объявлений.

- Booking creation and lifecycle management.
- Создание бронирований и управление их жизненным циклом.

- Reviews with cleanliness and location ratings.
- Отзывы с оценками чистоты и расположения.

- Listing statistics.
- Статистика по объявлениям.

- API documentation with Swagger and ReDoc.
- Документация API с использованием Swagger и ReDoc.

- Application, HTTP and database logging.
- Логирование приложения, HTTP-запросов и базы данных.

---

## Technologies
## Технологии

- Python 3.14
- Django 6.1.1
- Django REST Framework 3.18.1
- Django Filter
- Simple JWT
- drf-spectacular
- django-environ
- django-money
- django-simple-history
- Pillow
- SQLite / MySQL
- Docker / Docker Compose
- AWS S3

---

## Project Structure
## Структура проекта

```text
Project_Booking/
│
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml
│
├── config/
│
├── apps/
│   ├── listings/
│   ├── bookings/
│   ├── reviews/
│   ├── users/
│   └── statistic/
│
├── core/
│
├── media/
│
└── logs/
```

The project is divided into separate applications by business functionality.
Проект разделён на отдельные приложения по бизнес-функциональности.

---

## Installation
## Установка

Clone the repository.
Клонируйте репозиторий.

```bash
git clone <repository-url>
cd Project_Booking
```

Create and activate a virtual environment.
Создайте и активируйте виртуальное окружение.

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies.
Установите зависимости.

```bash
pip install -r requirements.txt
```

---

## Environment Variables
## Переменные окружения

Create a `.env` file in the project root.
Создайте файл `.env` в корневой директории проекта.

Example:
Пример:

```env
DEBUG=True
USE_S3=False

MYSQL=False

MYSQL_NAME=name
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_HOST=host_aws
MYSQL_PORT=3306
```

The `.env` file contains local configuration and must not be committed to Git.
Файл `.env` содержит локальные настройки и не должен добавляться в Git.

The `.env.example` file is used as a configuration template.
Файл `.env.example` используется как шаблон конфигурации.

---

## Database
## База данных

SQLite is used for local development.
Для локальной разработки используется SQLite.

MySQL can be enabled through the `MYSQL` environment variable.
MySQL можно включить через переменную окружения `MYSQL`.

```env
MYSQL=False
```

or:

```env
MYSQL=True
```

---

## Migrations
## Миграции

Create migrations:
Создать миграции:

```bash
python manage.py makemigrations
```

Apply migrations:
Применить миграции:

```bash
python manage.py migrate
```

---

## Run the Project
## Запуск проекта

Start the development server.
Запустите сервер разработки.

```bash
python manage.py runserver
```

The API will be available at:
API будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

---

## API Documentation
## Документация API

Swagger:
Swagger:

```text
http://127.0.0.1:8000/api/swagger/
```

ReDoc:
ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

OpenAPI schema:
OpenAPI-схема:

```text
http://127.0.0.1:8000/api/schema/
```

---

## Authentication
## Аутентификация

The API uses JWT authentication.
API использует JWT-аутентификацию.

Obtain tokens:
Получение токенов:

```http
POST /api/token/
```

Refresh token:
Обновление токена:

```http
POST /api/token/refresh/
```

Authenticated requests use:
Для авторизованных запросов используется:

```http
Authorization: Bearer <access-token>
```

---

## Main API
## Основные API

### Users
### Пользователи

```text
POST /api/users/register/
GET  /api/users/me/
PATCH /api/users/me/
DELETE /api/users/me/
```

### Listings
### Объявления

```text
GET    /api/listings/
POST   /api/listings/
GET    /api/listings/{id}/
PUT    /api/listings/{id}/
PATCH  /api/listings/{id}/
```

Listings support filtering, search, ordering and pagination.
Для объявлений доступны фильтрация, поиск, сортировка и пагинация.

### Bookings
### Бронирования

Bookings provide creation and lifecycle management.
Бронирования поддерживают создание и управление жизненным циклом.

### Reviews
### Отзывы

Reviews contain separate cleanliness and location ratings.
Отзывы содержат отдельные оценки чистоты и расположения.

### Statistics
### Статистика

The API provides booking and rating statistics for listings.
API предоставляет статистику бронирований и оценок объявлений.

---

## Logging
## Логирование

Application logs are stored in the `logs/` directory.
Логи приложения хранятся в директории `logs/`.

```text
logs/
├── http_logs.log
├── db_logs.log
└── application_logs.log
```

---

## Docker
## Docker

The project includes Docker configuration.
Проект содержит конфигурацию Docker.

```text
Dockerfile
docker-compose.yml
```

Docker can be used to run the project in a reproducible environment.
Docker может использоваться для запуска проекта в воспроизводимом окружении.

---

## Testing
## Тестирование

The project includes automated tests for the main business functionality.
Проект содержит автоматические тесты для основной бизнес-функциональности.

Tests cover models, serializers, services, ViewSets, permissions and business rules.
Тесты охватывают модели, сериализаторы, сервисы, ViewSet, права доступа и бизнес-правила.

---

## Project Status
## Статус проекта

The main backend functionality has been implemented and tested.
Основная backend-функциональность реализована и протестирована.

The project is prepared for further development, including improved API documentation, automated tests and production deployment.
Проект подготовлен для дальнейшего развития, включая улучшение документации API, автоматические тесты и production-развёртывание.

---

## License
## Лицензия

This project was created as a Django backend course final project.
Этот проект создан как итоговый backend-проект курса по Django.

The project is intended for educational purposes.
Проект предназначен для учебных целей.