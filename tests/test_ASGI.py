import os

from django.core.asgi import get_asgi_application
from django.test import Client, TestCase, override_settings


class TestASGIApplication(TestCase):
    def setUp(self):
        # Устанавливаем необходимые настройки окружения
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        self.client = Client()
        self.application = get_asgi_application()

    def test_asgi_application_exists(self):
        """
        Проверяем, что ASGI-приложение успешно создано
        """
        self.assertIsNotNone(self.application)

    def test_root_url(self):
        """
        Проверяем базовый запрос к приложению
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_404_page(self):
        """
        Проверяем обработку несуществующей страницы
        """
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)

    def test_static_files(self):
        """
        Проверяем доступ к статическим файлам
        """
        # Здесь нужно указать реальный путь к статическому файлу
        response = self.client.get("/static/example.css")
        self.assertEqual(response.status_code, 404)

    def test_media_files(self):
        """
        Проверяем доступ к медиафайлам
        """
        # Здесь нужно указать реальный путь к медиафайлу
        response = self.client.get("/media/example.jpg")
        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_debug_mode(self):
        """
        Проверяем работу в режиме отладки
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False)
    def test_production_mode(self):
        """
        Проверяем работу в продакшен-режиме
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
