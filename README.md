# fast_api_test_task

# FastAPI Department Management API

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI 0.115+](https://img.shields.io/badge/fastapi-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy 2.0+](https://img.shields.io/badge/sqlalchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 📋 Описание проекта

RESTful API для управления иерархической структурой отделов компании и сотрудниками. Проект построен на современном стеке технологий с использованием FastAPI, SQLAlchemy и Pydantic.

### 🎯 Возможности

- **Управление отделами**: CRUD операции с отделами, поддержка иерархической структуры
- **Управление сотрудниками**: Создание сотрудников с привязкой к отделам
- **Иерархическая структура**: Поддержка вложенности отделов с контролем глубины
- **Гибкое удаление**: Каскадное удаление или переназначение сотрудников при удалении отдела
- **Автоматическая документация**: Swagger UI и ReDoc документация API
- **Логирование**: Полное логирование всех операций
- **Docker поддержка**: Готовность к контейнеризации

## 🚀 Технологии

- **FastAPI** - Современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - Валидация данных и сериализация
- **Alembic** - Миграции базы данных
- **SQLite/PostgreSQL** - Поддержка различных БД
- **Pytest** - Тестирование
- **Docker** - Контейнеризация



# Простая сборка
docker build -t fastapi-app .

# Сборка без кэша
docker build --no-cache -t fastapi-app .

# Сборка с указанием Dockerfile
docker build -f Dockerfile -t fastapi-app .




# Запуск в фоновом режиме
docker run -d --name fastapi-container -p 8000:8000 fastapi-app

# Запуск с пробросом портов и монтированием томов
docker run -d \
  --name fastapi-container \
  -p 8000:8000 \
  -v $(pwd)/app.db:/app/app.db \
  -v $(pwd)/logs:/app/logs \
  -e DEBUG=True \
  fastapi-app

# Запуск в интерактивном режиме (для отладки)
docker run -it --rm -p 8000:8000 fastapi-app



# Запуск с docker-compose
docker-compose up -d

# Запуск с пересборкой
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Остановка с удалением томов
docker-compose down -v
