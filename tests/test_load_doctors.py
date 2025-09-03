import json
import os

from django.core.management import call_command
from django.test import TestCase

from medsite.models import Doctor, Schedule
from users.models import CustomUser


class TestLoadDoctorsCommand(TestCase):
    def setUp(self):
        # Создаем тестовый JSON файл
        self.test_data = [
            {
                "fields": {
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "specialization": "рентген",
                    "middle_name": "Иванович",
                    "equipment_type": "рентген-аппарат",
                    "description": "Опытный врач",
                    "is_active": True,
                }
            },
            {
                "fields": {
                    "first_name": "Петр",
                    "last_name": "Петров",
                    "specialization": "узи",
                }
            },
        ]

        self.test_file = "test_doctors.json"
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        # Удаляем тестовый файл
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_valid_file(self):
        call_command("load_doctors", self.test_file)

        # Проверяем создание пользователей
        self.assertEqual(CustomUser.objects.count(), 2)

        # Проверяем создание профилей врачей
        self.assertEqual(Doctor.objects.count(), 2)

        # Проверяем создание расписаний
        self.assertEqual(Schedule.objects.count(), 5 + 6)

    def test_missing_required_fields(self):
        invalid_data = [
            {
                "fields": {
                    "first_name": "Иван",  # Отсутствуют last_name и specialization
                }
            }
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with self.assertRaises(ValueError) as context:
            call_command("load_doctors", self.test_file)
        self.assertEqual(str(context.exception), "Отсутствуют обязательные поля")

    def test_empty_json_file(self):
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump([], f)

        call_command("load_doctors", self.test_file)
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertEqual(Doctor.objects.count(), 0)
        self.assertEqual(Schedule.objects.count(), 0)

    def test_invalid_json_structure(self):
        # Проверяем обработку некорректной структуры JSON
        invalid_data = [
            {"missing_fields": "data"},
            {"fields": {"missing_required_fields": "value"}},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with self.assertRaises(ValueError):
            call_command("load_doctors", self.test_file)
