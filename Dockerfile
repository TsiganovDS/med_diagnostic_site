FROM python:3.12.3

# Включаем немедленное выполнение вывода программы
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Обновляем список пакетов и устанавливаем curl и gnupg для загрузки Poetry
RUN apt-get update
RUN apt-get install -y curl gnupg

# Загружаем и устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Копируем файл с зависимостями и устанавливаем их
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Копируем остальные файлы проекта в контейнер
COPY . .


# Порт, который будет использовать контейнер
EXPOSE 8000


# Определяем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]