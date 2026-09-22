# Project Booking

[English](#english) | [Русский](#русский)

---

<a id="english"></a>
# English

Backend REST API for apartment rental and booking management, built with Django and Django REST Framework.

The project was created as a final Django backend course project and includes authentication, apartment listings, photo uploads, booking workflows, reviews, statistics, audit history, testing, Docker support, and deployment on AWS.

---

## Features

### Users and authentication

- Custom user model with **email as the login identifier**
- User registration and profile management
- JWT authentication with access and refresh tokens
- Refresh token rotation and blacklist support
- Soft account deactivation instead of physical deletion
- Account deactivation is blocked while open bookings exist
- Active listings owned by a deactivated user are automatically deactivated

### Listings

- Apartment rental listings
- European country choices
- Address fields: country, city, district, street, house number, apartment number
- Room choices: `1`, `2`, `3`, `4`, `5`, `5+`
- Price per night stored with `django-money`
- Public listing browsing
- Filtering, search, ordering and pagination
- Owner-only create/update/delete operations
- `my-listings` endpoint for the authenticated owner
- Review count and average cleanliness/location ratings included in listing responses
- Soft deletion with a **180-day restoration period**
- Listings with pending or confirmed bookings cannot be deleted
- Automatic cleanup support for old soft-deleted listings

### Listing photos

- Separate photo model linked to listings
- Multipart/form-data uploads
- Maximum **10 photos per listing**
- Only the listing owner can upload or modify photos
- Uploaded files are stored in local media storage
- Listing responses include related photos

### Bookings

Booking lifecycle:

```text
PENDING
├── CONFIRMED ──> COMPLETED
├── REJECTED
└── CANCELLED
```

Implemented booking rules include:

- A tenant cannot book their own listing
- Only active and non-deleted listings can be booked
- Booking dates cannot overlap existing `PENDING` or `CONFIRMED` bookings
- Database transaction and `select_for_update()` are used to reduce race-condition risk
- Bookings can be created up to **365 days ahead**
- Check-in window: **14:00–22:00**
- Check-out window: **07:00–11:00**
- Cancellation deadline: **24 hours before check-in**
- Listing and tenant data are stored as booking snapshots so historical bookings remain readable even if related data later changes
- Listing owners can confirm or reject pending bookings
- Tenants can cancel their own bookings
- Finished confirmed bookings can be marked as completed
- Separate endpoints are provided for:
  - tenant trips
  - active/current trips
  - past trips
  - bookings received for the owner's listings

### Reviews

- Reviews are linked one-to-one with bookings
- Only the tenant who made the booking can leave a review
- Reviews can only be created for completed bookings
- Finished confirmed bookings are automatically completed when appropriate before review creation
- One review per booking
- Separate ratings from `1` to `5` for:
  - cleanliness
  - location
- Optional review comment
- Public review listing and detail access
- Review history is preserved with `django-simple-history`

### Statistics

Public listing statistics:

- number of reviews
- average cleanliness rating
- average location rating

Private owner statistics:

- available only to the listing owner
- review statistics
- booking statistics

Invalid listing UUIDs are handled as normal API `404` responses instead of server errors.

### API infrastructure

- Business API implemented with DRF **ViewSets**
- Router-based business endpoints
- Swagger UI and ReDoc documentation
- OpenAPI schema generated with `drf-spectacular`
- Page-number pagination
- Anonymous and authenticated request throttling
- Application, HTTP and database logging
- Model history with `django-simple-history`

---

## Technologies

- Python **3.14** for local development
- Python **3.13-slim** in Docker
- Django **6.1.1**
- Django REST Framework **3.18.1**
- Simple JWT
- drf-spectacular
- django-filter
- django-environ
- django-money
- django-simple-history
- Pillow
- mysqlclient
- pytest
- pytest-django
- pytest-cov
- Faker
- SQLite
- MySQL **8.4**
- Docker / Docker Compose
- AWS EC2

Media files currently use Django `FileSystemStorage`; AWS S3 is not used.

---

## Project structure

```text
Project_Booking/
│
├── manage.py
├── requirements.txt
├── pytest.ini
├── conftest.py
├── .env
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── constants.py
│   ├── models.py
│   ├── validators.py
│   └── management/
│       └── commands/
│
├── apps/
│   ├── users/
│   ├── listings/
│   ├── bookings/
│   ├── reviews/
│   └── statistic/
│
├── media/
├── static/
└── logs/
```

The project is separated into Django applications by business responsibility.

---

## Local installation

Clone the repository:

```bash
git clone https://github.com/VNMad/Project_Booking.git
cd Project_Booking
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from the example:

```bash
copy .env.example .env
```

For local SQLite development:

```env
MYSQL=False
POSTGRES=False
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

## Environment variables

Example configuration:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DEFAULT_FROM_EMAIL=no-reply@booking.local
DEMO_USER_PASSWORD=change-me

MYSQL=False
MYSQL_ENGINE=django.db.backends.mysql
MYSQL_NAME=booking_db
MYSQL_USER=booking_user
MYSQL_PASSWORD=change-me
MYSQL_ROOT_PASSWORD=change-me
MYSQL_HOST=db
MYSQL_PORT=3306

POSTGRES=False

DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=change-me
```

Do not commit the real `.env` file.

> `MYSQL_ROOT_PASSWORD` is required by the current Docker Compose MySQL service.

---

## Database

### SQLite

SQLite is used when neither MySQL nor PostgreSQL is enabled:

```env
MYSQL=False
POSTGRES=False
```

### MySQL

Enable MySQL with:

```env
MYSQL=True
MYSQL_ENGINE=django.db.backends.mysql
MYSQL_NAME=booking_db
MYSQL_USER=booking_user
MYSQL_PASSWORD=change-me
MYSQL_ROOT_PASSWORD=change-me
MYSQL_HOST=db
MYSQL_PORT=3306
```

The Docker Compose configuration uses **MySQL 8.4** and stores database data in a named Docker volume.

---

## Migrations

This project currently generates application migrations in the target environment.

Create migrations explicitly:

```bash
python manage.py makemigrations users
python manage.py makemigrations listings
python manage.py makemigrations bookings
python manage.py makemigrations reviews
python manage.py makemigrations statistic
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

---

## Run locally

Start the development server:

```bash
python manage.py runserver
```

API base URL:

```text
http://127.0.0.1:8000/
```

---

## API documentation

Swagger UI:

```text
http://127.0.0.1:8000/api/swagger/
```

ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

---

## Authentication

Obtain JWT tokens:

```http
POST /api/token/
```

Refresh token:

```http
POST /api/token/refresh/
```

Authenticated requests use:

```http
Authorization: Bearer <access-token>
```

Current JWT settings:

- access token lifetime: **60 minutes**
- refresh token lifetime: **1 day**
- refresh token rotation: enabled
- blacklist after rotation: enabled

---

## Main API endpoints

### Users

```http
POST   /api/users/register/
GET    /api/users/me/
PATCH  /api/users/me/
DELETE /api/users/me/
```

### Listings

```http
GET    /api/listings/
POST   /api/listings/
GET    /api/listings/{id}/
PUT    /api/listings/{id}/
PATCH  /api/listings/{id}/
DELETE /api/listings/{id}/

GET    /api/listings/my-listings/
POST   /api/listings/{id}/restore/
```

Listing search:

```http
GET /api/listings/?search=berlin
```

Ordering examples:

```http
GET /api/listings/?ordering=price_per_night
GET /api/listings/?ordering=-created_at
```

### Photos

```http
GET    /api/listings/photos/
POST   /api/listings/photos/
GET    /api/listings/photos/{id}/
PUT    /api/listings/photos/{id}/
PATCH  /api/listings/photos/{id}/
DELETE /api/listings/photos/{id}/
```

Photo creation uses `multipart/form-data`.

### Bookings

```http
POST /api/bookings/
GET  /api/bookings/{id}/

GET  /api/bookings/my-trips/
GET  /api/bookings/my-trips/?period=active
GET  /api/bookings/my-trips/?period=past
GET  /api/bookings/my-listings/

POST /api/bookings/{id}/confirm/
POST /api/bookings/{id}/reject/
POST /api/bookings/{id}/cancel/
```

The default base booking list endpoint is intentionally not exposed as a general booking list.

### Reviews

```http
GET    /api/reviews/
POST   /api/reviews/
GET    /api/reviews/{id}/
PUT    /api/reviews/{id}/
PATCH  /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

### Statistics

Public rating statistics:

```http
GET /api/statistics/listings/{id}/
```

Private owner statistics:

```http
GET /api/statistics/listings/{id}/owner/
```

---

## Demo data

A deterministic demo-data command is included for presentations:

```bash
python manage.py seed2_demo_data
```

It creates:

```text
2 owners
5 tenants
4 apartment listings
24 bookings
12 reviews
```

For every listing, the command creates:

```text
3 COMPLETED bookings
1 CONFIRMED booking
1 REJECTED booking
1 CANCELLED booking
```

Each completed booking has one review, so every listing receives three reviews.

The same password is read from:

```env
DEMO_USER_PASSWORD=...
```

The generated listing titles and demo comments end with:

```text
[DEMO]
```

Running the command again removes the previous `seed2_demo_data` dataset before recreating it.

---

## Docker

Build and start MySQL:

```bash
docker compose build
docker compose up -d db
```

Check the database container:

```bash
docker compose ps
```

Create and apply migrations:

```bash
docker compose run --rm web python manage.py makemigrations users
docker compose run --rm web python manage.py makemigrations listings
docker compose run --rm web python manage.py makemigrations bookings
docker compose run --rm web python manage.py makemigrations reviews
docker compose run --rm web python manage.py makemigrations statistic
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
```

Collect static files:

```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

Start the application:

```bash
docker compose up -d
```

The Django development server is exposed on:

```text
http://localhost:8000/
```

The current Docker setup intentionally uses Django `runserver` for the course/demo deployment.

---

## AWS deployment

The project is currently deployable on AWS EC2 using Docker Compose.

Current deployment architecture:

```text
AWS EC2
│
├── Docker
│   ├── booking_django
│   │   └── Django REST API :8000
│   │
│   └── booking_db
│       └── MySQL 8.4
│
├── named MySQL volume
├── media volume
├── static volume
└── logs volume
```

MySQL port `3306` is not published publicly by Docker Compose.

Application access should be restricted using the EC2 Security Group as appropriate for the deployment.

---

## Media files

Uploaded listing photos are stored using Django local filesystem storage:

```text
media/
└── listings/
```

Relevant settings:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

In development, Django serves media files when `DEBUG=True`.

---

## Logging

The application uses rotating log files:

```text
logs/
├── application_logs.log
├── http_logs.log
└── db_logs.log
```

Container logs can also be viewed with:

```bash
docker compose logs -f web
```

---

## API limits

Default pagination:

```text
10 objects per page
```

Default throttling:

```text
Anonymous users:       5 requests/minute
Authenticated users:   1000 requests/day
```

---

## Testing

Run the complete test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=apps --cov=core
```

The test suite covers the main business layers, including:

- models
- serializers
- services
- ViewSets
- permissions
- booking lifecycle rules
- overlapping booking protection
- listing soft deletion/restoration
- reviews
- statistics
- signals
- management commands

---

## Important business rules

| Area | Rule |
|---|---|
| Authentication | Email is used as the login identifier |
| Listings | Only the owner can modify a listing |
| Listings | Maximum 10 photos |
| Listings | Soft-deleted listings can be restored for 180 days |
| Listings | Listings with active pending/confirmed bookings cannot be deleted |
| Booking | A user cannot book their own listing |
| Booking | Overlapping pending/confirmed bookings are rejected |
| Booking | Booking horizon is limited to 365 days |
| Booking | Check-in is allowed from 14:00 to 22:00 |
| Booking | Check-out is allowed from 07:00 to 11:00 |
| Booking | Cancellation must be made at least 24 hours before check-in |
| Review | Only the booking tenant can leave a review |
| Review | Reviews are allowed only for completed bookings |
| Review | Only one review is allowed per booking |
| Statistics | Public rating statistics are available for active listings |
| Statistics | Extended statistics are available only to the listing owner |

---

## Project status

The main backend functionality is implemented and tested.

The current version includes:

- authentication
- listings
- listing photos
- booking lifecycle
- booking snapshots
- reviews
- public/private statistics
- soft deletion/restoration
- model history
- logging
- Swagger/ReDoc
- demo data generation
- Docker Compose
- MySQL deployment
- AWS EC2 deployment

---

## License / purpose

This repository was created as an educational Django backend project.

It is intended for learning, demonstration, testing and portfolio purposes.


---

<a id="русский"></a>
# Русский

# Project Booking

Backend REST API для аренды апартаментов и управления бронированиями, созданный на Django и Django REST Framework.

Проект разработан как итоговый учебный Django backend-проект и включает аутентификацию, объявления об аренде, загрузку фотографий, жизненный цикл бронирований, отзывы, статистику, историю изменений, тестирование, Docker и развертывание на AWS.

---

## Возможности

### Пользователи и аутентификация

- Кастомная модель пользователя с **email в качестве логина**
- Регистрация пользователя и управление профилем
- JWT-аутентификация с access и refresh токенами
- Ротация refresh-токенов и blacklist
- Мягкая деактивация аккаунта вместо физического удаления
- Деактивация аккаунта блокируется, если есть незавершенные бронирования
- Активные объявления деактивированного владельца автоматически становятся неактивными

### Объявления

- Объявления о сдаче апартаментов
- Выбор страны из списка европейских стран
- Адрес: страна, город, район, улица, номер дома, номер квартиры
- Количество комнат: `1`, `2`, `3`, `4`, `5`, `5+`
- Цена за ночь хранится через `django-money`
- Публичный просмотр объявлений
- Фильтрация, поиск, сортировка и пагинация
- Создание, изменение и удаление только владельцем
- Endpoint `my-listings` для авторизованного владельца
- В ответе объявления возвращаются количество отзывов и средние оценки чистоты/расположения
- Soft delete с **периодом восстановления 180 дней**
- Объявление нельзя удалить, если есть активные `PENDING` или `CONFIRMED` бронирования
- Поддерживается автоматическое физическое удаление старых soft-deleted объявлений

### Фотографии объявлений

- Отдельная модель фотографий, связанная с объявлением
- Загрузка через `multipart/form-data`
- Максимум **10 фотографий на объявление**
- Загружать и изменять фотографии может только владелец объявления
- Файлы сохраняются в локальном media storage
- Фотографии возвращаются внутри ответа объявления

### Бронирования

Жизненный цикл бронирования:

```text
PENDING
├── CONFIRMED ──> COMPLETED
├── REJECTED
└── CANCELLED
```

Реализованные правила:

- Арендатор не может забронировать собственное объявление
- Можно бронировать только активные и не удаленные объявления
- Даты не могут пересекаться с существующими `PENDING` или `CONFIRMED` бронированиями
- Для снижения риска race condition используются транзакция и `select_for_update()`
- Бронирование возможно максимум на **365 дней вперед**
- Время check-in: **14:00–22:00**
- Время check-out: **07:00–11:00**
- Отмена возможна не позднее чем за **24 часа до check-in**
- Данные объявления и арендатора сохраняются в snapshot-полях Booking, поэтому история сохраняется даже после изменения связанных объектов
- Владелец может подтвердить или отклонить `PENDING` бронирование
- Арендатор может отменить собственное бронирование
- Завершенные подтвержденные бронирования могут переводиться в `COMPLETED`
- Отдельные endpoint'ы для:
  - поездок арендатора
  - активных поездок
  - прошлых поездок
  - бронирований, полученных владельцем по своим объявлениям

### Отзывы

- Один отзыв связан с одним Booking через OneToOne
- Оставить отзыв может только арендатор этого бронирования
- Отзыв можно создать только для `COMPLETED` бронирования
- Завершившееся `CONFIRMED` бронирование при необходимости автоматически переводится в `COMPLETED` перед созданием отзыва
- Один отзыв на одно бронирование
- Отдельные оценки от `1` до `5`:
  - чистота
  - расположение
- Комментарий необязателен
- Список и detail отзывов доступны публично
- История изменений отзывов сохраняется через `django-simple-history`

### Статистика

Публичная статистика объявления:

- количество отзывов
- средняя оценка чистоты
- средняя оценка расположения

Приватная статистика владельца:

- доступна только владельцу объявления
- статистика отзывов
- статистика бронирований

Некорректный UUID объявления обрабатывается как обычный API `404`, без server error.

### API-инфраструктура

- Business API реализован через DRF **ViewSets**
- Router-based endpoints
- Swagger UI и ReDoc
- OpenAPI schema через `drf-spectacular`
- Page-number pagination
- Throttling для anonymous и authenticated пользователей
- Логирование приложения, HTTP и базы данных
- История моделей через `django-simple-history`

---

## Технологии

- Python **3.14** локально
- Python **3.13-slim** в Docker
- Django **6.1.1**
- Django REST Framework **3.18.1**
- Simple JWT
- drf-spectacular
- django-filter
- django-environ
- django-money
- django-simple-history
- Pillow
- mysqlclient
- pytest
- pytest-django
- pytest-cov
- Faker
- SQLite
- MySQL **8.4**
- Docker / Docker Compose
- AWS EC2

Media-файлы сейчас хранятся через Django `FileSystemStorage`; AWS S3 не используется.

---

## Структура проекта

```text
Project_Booking/
│
├── manage.py
├── requirements.txt
├── pytest.ini
├── conftest.py
├── .env
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── constants.py
│   ├── models.py
│   ├── validators.py
│   └── management/
│       └── commands/
│
├── apps/
│   ├── users/
│   ├── listings/
│   ├── bookings/
│   ├── reviews/
│   └── statistic/
│
├── media/
├── static/
└── logs/
```

Проект разделен на Django-приложения по зонам ответственности.

---

## Локальная установка

Клонировать репозиторий:

```bash
git clone https://github.com/VNMad/Project_Booking.git
cd Project_Booking
```

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать на Windows:

```powershell
.venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Создать `.env` на основе примера:

```bash
copy .env.example .env
```

Для локальной разработки на SQLite:

```env
MYSQL=False
POSTGRES=False
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

## Переменные окружения

Пример:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DEFAULT_FROM_EMAIL=no-reply@booking.local
DEMO_USER_PASSWORD=change-me

MYSQL=False
MYSQL_ENGINE=django.db.backends.mysql
MYSQL_NAME=booking_db
MYSQL_USER=booking_user
MYSQL_PASSWORD=change-me
MYSQL_ROOT_PASSWORD=change-me
MYSQL_HOST=db
MYSQL_PORT=3306

POSTGRES=False

DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=change-me
```

Не добавляйте реальный `.env` в Git.

> `MYSQL_ROOT_PASSWORD` требуется текущему MySQL-сервису в Docker Compose.

---

## База данных

### SQLite

SQLite используется, когда MySQL и PostgreSQL отключены:

```env
MYSQL=False
POSTGRES=False
```

### MySQL

Для MySQL:

```env
MYSQL=True
MYSQL_ENGINE=django.db.backends.mysql
MYSQL_NAME=booking_db
MYSQL_USER=booking_user
MYSQL_PASSWORD=change-me
MYSQL_ROOT_PASSWORD=change-me
MYSQL_HOST=db
MYSQL_PORT=3306
```

Docker Compose использует **MySQL 8.4**, а данные базы хранятся в именованном Docker volume.

---

## Миграции

В текущей конфигурации проекта migrations для приложений создаются в целевом окружении.

Создание:

```bash
python manage.py makemigrations users
python manage.py makemigrations listings
python manage.py makemigrations bookings
python manage.py makemigrations reviews
python manage.py makemigrations statistic
python manage.py makemigrations
```

Применение:

```bash
python manage.py migrate
```

---

## Локальный запуск

```bash
python manage.py runserver
```

API:

```text
http://127.0.0.1:8000/
```

---

## API-документация

Swagger UI:

```text
http://127.0.0.1:8000/api/swagger/
```

ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

---

## Аутентификация

Получение JWT:

```http
POST /api/token/
```

Обновление токена:

```http
POST /api/token/refresh/
```

Авторизованный запрос:

```http
Authorization: Bearer <access-token>
```

Текущие настройки:

- access token: **60 минут**
- refresh token: **1 день**
- rotation refresh token: включена
- blacklist after rotation: включен

---

## Основные API endpoints

### Users

```http
POST   /api/users/register/
GET    /api/users/me/
PATCH  /api/users/me/
DELETE /api/users/me/
```

### Listings

```http
GET    /api/listings/
POST   /api/listings/
GET    /api/listings/{id}/
PUT    /api/listings/{id}/
PATCH  /api/listings/{id}/
DELETE /api/listings/{id}/

GET    /api/listings/my-listings/
POST   /api/listings/{id}/restore/
```

Поиск:

```http
GET /api/listings/?search=berlin
```

Сортировка:

```http
GET /api/listings/?ordering=price_per_night
GET /api/listings/?ordering=-created_at
```

### Photos

```http
GET    /api/listings/photos/
POST   /api/listings/photos/
GET    /api/listings/photos/{id}/
PUT    /api/listings/photos/{id}/
PATCH  /api/listings/photos/{id}/
DELETE /api/listings/photos/{id}/
```

Создание фотографии использует `multipart/form-data`.

### Bookings

```http
POST /api/bookings/
GET  /api/bookings/{id}/

GET  /api/bookings/my-trips/
GET  /api/bookings/my-trips/?period=active
GET  /api/bookings/my-trips/?period=past
GET  /api/bookings/my-listings/

POST /api/bookings/{id}/confirm/
POST /api/bookings/{id}/reject/
POST /api/bookings/{id}/cancel/
```

Общий `GET /api/bookings/` намеренно не предоставляется как публичный список всех бронирований.

### Reviews

```http
GET    /api/reviews/
POST   /api/reviews/
GET    /api/reviews/{id}/
PUT    /api/reviews/{id}/
PATCH  /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

### Statistics

Публичная статистика:

```http
GET /api/statistics/listings/{id}/
```

Приватная статистика владельца:

```http
GET /api/statistics/listings/{id}/owner/
```

---

## Demo-данные

Для презентации есть детерминированная команда:

```bash
python manage.py seed2_demo_data
```

Она создает:

```text
2 owners
5 tenants
4 apartment listings
24 bookings
12 reviews
```

Для каждого объявления:

```text
3 COMPLETED bookings
1 CONFIRMED booking
1 REJECTED booking
1 CANCELLED booking
```

Каждое `COMPLETED` бронирование получает отзыв, поэтому у каждого объявления создается по три отзыва.

Общий пароль берется из:

```env
DEMO_USER_PASSWORD=...
```

Названия demo-объявлений и demo-комментарии заканчиваются на:

```text
[DEMO]
```

Повторный запуск удаляет предыдущие данные `seed2_demo_data` и создает их заново.

---

## Docker

Сборка и запуск MySQL:

```bash
docker compose build
docker compose up -d db
```

Проверка:

```bash
docker compose ps
```

Создание и применение migrations:

```bash
docker compose run --rm web python manage.py makemigrations users
docker compose run --rm web python manage.py makemigrations listings
docker compose run --rm web python manage.py makemigrations bookings
docker compose run --rm web python manage.py makemigrations reviews
docker compose run --rm web python manage.py makemigrations statistic
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
```

Static:

```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

Запуск приложения:

```bash
docker compose up -d
```

Django development server доступен:

```text
http://localhost:8000/
```

Текущий Docker deployment специально использует Django `runserver` для учебной/demo-среды.

---

## Развертывание на AWS

Проект разворачивается на AWS EC2 через Docker Compose.

Текущая схема:

```text
AWS EC2
│
├── Docker
│   ├── booking_django
│   │   └── Django REST API :8000
│   │
│   └── booking_db
│       └── MySQL 8.4
│
├── named MySQL volume
├── media volume
├── static volume
└── logs volume
```

Порт MySQL `3306` не публикуется наружу через Docker Compose.

Доступ к приложению рекомендуется ограничивать через EC2 Security Group.

---

## Media-файлы

Фотографии объявлений хранятся локально:

```text
media/
└── listings/
```

Настройки:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

При `DEBUG=True` Django может отдавать media-файлы в development-режиме.

---

## Логирование

Используются rotating log files:

```text
logs/
├── application_logs.log
├── http_logs.log
└── db_logs.log
```

Логи контейнера:

```bash
docker compose logs -f web
```

---

## Ограничения API

Пагинация:

```text
10 объектов на страницу
```

Throttling:

```text
Anonymous users:       5 запросов/минуту
Authenticated users:   1000 запросов/день
```

---

## Тестирование

Запустить все тесты:

```bash
pytest
```

С coverage:

```bash
pytest --cov=apps --cov=core
```

Тестами покрываются основные бизнес-слои:

- models
- serializers
- services
- ViewSets
- permissions
- lifecycle бронирований
- защита от пересечений
- soft delete / restore объявлений
- reviews
- statistics
- signals
- management commands

---

## Основные бизнес-правила

| Область | Правило |
|---|---|
| Authentication | Email используется как логин |
| Listings | Изменять объявление может только владелец |
| Listings | Максимум 10 фотографий |
| Listings | Soft-deleted объявление можно восстановить в течение 180 дней |
| Listings | Объявление с активным pending/confirmed booking нельзя удалить |
| Booking | Нельзя бронировать собственное объявление |
| Booking | Пересекающиеся pending/confirmed бронирования запрещены |
| Booking | Максимальный горизонт бронирования — 365 дней |
| Booking | Check-in разрешен с 14:00 до 22:00 |
| Booking | Check-out разрешен с 07:00 до 11:00 |
| Booking | Отмена минимум за 24 часа до check-in |
| Review | Отзыв может оставить только tenant бронирования |
| Review | Отзыв разрешен только для completed booking |
| Review | Один отзыв на одно бронирование |
| Statistics | Публичная статистика доступна для активных объявлений |
| Statistics | Расширенная статистика доступна только владельцу |

---

## Статус проекта

Основная backend-функциональность реализована и протестирована.

Текущая версия включает:

- authentication
- listings
- listing photos
- booking lifecycle
- booking snapshots
- reviews
- public/private statistics
- soft delete / restore
- model history
- logging
- Swagger / ReDoc
- demo data generation
- Docker Compose
- MySQL deployment
- AWS EC2 deployment

---

## Назначение

Репозиторий создан как учебный Django backend-проект.

Он предназначен для обучения, демонстрации, тестирования и использования в портфолио.

