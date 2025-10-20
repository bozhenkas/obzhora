# базовый образ
FROM python:3.11-slim

# не буферим вывод, отключаем кэш pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# системные зависимости для asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# копируем и апгрейдим pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# копируем код
COPY ./src ./src

# пусть питон видит пакеты из src
ENV PYTHONPATH=/app/src

# запускаем главный файл как модуль
CMD ["python", "-m", "main"]