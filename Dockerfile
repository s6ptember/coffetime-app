# Dockerfile
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements файл
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем необходимые директории
RUN mkdir -p app/coffeeshop/static/images/products \
    && mkdir -p media \
    && mkdir -p staticfiles

# Устанавливаем права доступа
RUN chmod -R 755 app/coffeeshop/static \
    && chmod -R 755 media \
    && chmod -R 755 staticfiles

# Экспортируем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
