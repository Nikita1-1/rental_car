FROM python:3.11


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы из текущей директории
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN python manage.py collectstatic --noinput

# Запускаем Gunicorn
CMD ["gunicorn", "rental_car.wsgi:application", "--bind", "0.0.0.0:8000"]
