import json
import os

from django.core.management import call_command
from django.test import TestCase

from medsite.models import Service, ServiceCategory


class TestImportServicesCommand(TestCase):
    def setUp(self):
        self.test_file = "test_services.json"
        self.test_data = [
            {
                "model": "medsite.ServiceCategory",
                "pk": 1,
                "fields": {"name": "Диагностика", "slug": "diagnostika"},
            },
            {
                "model": "medsite.Service",
                "pk": 1,
                "fields": {
                    "category": 1,
                    "name": "УЗИ брюшной полости",
                    "description": "Ультразвуковое исследование",
                    "price": 2500,
                },
            },
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_valid_import(self):
        call_command("import_services", self.test_file)

        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 1)

    def test_empty_file(self):
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump([], f)

        call_command("import_services", self.test_file)
        self.assertEqual(ServiceCategory.objects.count(), 0)
        self.assertEqual(Service.objects.count(), 0)
