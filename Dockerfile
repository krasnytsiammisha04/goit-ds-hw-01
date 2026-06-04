# Використовуємо легкий образ Python
FROM python:3.10-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо всі файли з папки проєкту в контейнер
COPY . .

# Встановлюємо Poetry
RUN pip install poetry

# Конфігуруємо Poetry, щоб він не створював віртуальне середовище в контейнері
RUN poetry config virtualenvs.create false

# Встановлюємо залежності проєкту
RUN poetry install --no-root

# Команда для запуску твого помічника
CMD ["python", "main.py"]