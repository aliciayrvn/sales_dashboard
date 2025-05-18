# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app /app

# Копируем скрипт ожидания PostgreSQL
COPY app/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Команда по умолчанию — ждем БД, потом запускаем миграции
CMD ["/wait-for-db.sh", "python", "manage.py", "migrate"]
