import json

from django.core.management.base import BaseCommand

from medsite.models import Service, ServiceCategory


class Command(BaseCommand):
    help = "Импортирует услуги и категории из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Путь к JSON файлу")

    def handle(self, *args, **kwargs):
        json_file = kwargs["json_file"]

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            categories = {}
            for item in data:
                if item["model"] == "medsite.ServiceCategory":
                    category, created = ServiceCategory.objects.get_or_create(
                        name=item["fields"]["name"], slug=item["fields"]["slug"]
                    )
                    categories[item["fields"]["name"]] = category

            for item in data:
                if item["model"] == "medsite.Service":

                    category_id = item["fields"]["category"]
                    category = ServiceCategory.objects.get(id=category_id)

                    Service.objects.create(
                        category=category,
                        name=item["fields"]["name"],
                        description=item["fields"]["description"],
                        price=item["fields"]["price"],
                        duration_minutes=30,
                    )

            self.stdout.write(self.style.SUCCESS("Данные успешно импортированы"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Файл {json_file} не найден"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при импорте: {str(e)}"))
