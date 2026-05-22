@echo off
REM Сборка образа
docker build -t fastapi-app .

REM Остановка и удаление старого контейнера (если есть)
docker stop fastapi-container 2>nul
docker rm fastapi-container 2>nul

REM Запуск нового контейнера
docker run -d --name fastapi-container -p 8000:8000 -v %cd%\app.db:/app/app.db -v %cd%\logs:/app/logs fastapi-app

echo FastAPI приложение запущено на http://localhost:8000
echo Документация: http://localhost:8000/docs