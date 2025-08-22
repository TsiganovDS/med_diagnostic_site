import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
User = get_user_model()
from medsite.models import Doctor, Schedule
from datetime import time
import logging
import calendar
from django.db import IntegrityError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Загружает врачей из JSON-файла'

    SCHEDULE_TEMPLATES = {
        'рентген': {
            'weekdays': [0, 1, 2, 3, 4],  # Пн-Пт
            'start_time': time(8, 0),
            'end_time': time(17, 0)
        },
        'узи': {
            'weekdays': [0, 1, 2, 3, 4, 5],  # Пн-Сб
            'start_time': time(8, 0),
            'end_time': time(20, 0)
        },
        'экг': {
            'weekdays': [0, 1, 2, 3, 4],  # Пн-Пт
            'start_time': time(8, 0),
            'end_time': time(16, 0)
        },
        'по умолчанию': {
            'weekdays': [0, 1, 2, 3, 4],  # Пн-Пт
            'start_time': time(9, 0),
            'end_time': time(18, 0)
        }
    }

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к JSON-файлу')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        fields = None
        success_count = 0
        error_count = 0

        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                doctors_data = json.load(file)
        except FileNotFoundError:
            self.stderr.write(f"Файл {json_file} не найден")
            return
        except json.JSONDecodeError:
            self.stderr.write("Ошибка при чтении JSON-файла")
            return

        logger.info(f"Загружено {len(doctors_data)} записей для обработки")

        for doctor_data in doctors_data:
            fields = doctor_data.get('fields', {})
            # Валидация обязательных полей
            if not self.validate_doctor_data(fields):
                raise ValueError("Отсутствуют обязательные поля")

            # Создание пользователя
            user = User.objects.create(
                first_name=fields.get('first_name', ''),
                last_name=fields.get('last_name', ''),
                email=f"{fields.get('first_name', '').lower()}.{fields.get('last_name', '').lower()}@example.com",
                is_staff=True
            )

            # Создание профиля врача
            doctor = Doctor.objects.create(
                user=user,
                first_name=fields.get('first_name', ''),
                last_name=fields.get('last_name', ''),
                middle_name=fields.get('middle_name', ''),
                equipment_type=fields.get('equipment_type', ''),
                specialization=fields.get('specialization', ''),
                description=fields.get('description', ''),
                is_active=fields.get('is_active', True)
            )

            # Определение шаблона расписания
            specialization = fields.get('specialization', '').lower()
            schedule_template = self.get_specialization_template(specialization)

            # Создание записей расписания
            if schedule_template:
                try:
                    for weekday in schedule_template['weekdays']:
                        Schedule.objects.create(
                            doctor=doctor,
                            weekday=weekday,
                            start_time=schedule_template['start_time'],
                            end_time=schedule_template['end_time'],
                            is_active=True
                        )
                        success_count += 1
                        self.stdout.write(
                            f"Успешно создано расписание для врача {fields.get('first_name', '')} {fields.get('last_name', '')}"
                        )
                except IntegrityError as e:
                    logger.error(f"Ошибка целостности данных при создании расписания: {str(e)}")
                    self.stderr.write(f"Ошибка: {str(e)}")
                    error_count += 1
                except Exception as e:
                    logger.error(f"Ошибка при обработке данных врача: {str(e)}")
                    self.stderr.write(
                        f"Ошибка при обработке данных врача {fields.get('last_name', 'Неизвестно')}: {str(e)}"
                    )
                    error_count += 1
            else:
                logger.warning(
                    f"Не удалось определить шаблон расписания для врача {fields.get('last_name', '')}"
                )
                error_count += 1

            self.stdout.write(f"\nУспехов: {success_count}, ошибок: {error_count}\n")

    def validate_doctor_data(self, fields):
        """Проверка обязательных полей"""
        required_fields = ['first_name', 'last_name', 'specialization']
        for field in required_fields:
            if not fields.get(field):
                return False
        return True

    def get_specialization_template(self, specialization):
        """Получение шаблона расписания по специализации"""
        specialization = specialization.lower()
        if 'рентген' in specialization:
            return self.SCHEDULE_TEMPLATES['рентген']
        elif 'узи' in specialization:
            return self.SCHEDULE_TEMPLATES['узи']
        elif 'экг' in specialization:
            return self.SCHEDULE_TEMPLATES['экг']
        return self.SCHEDULE_TEMPLATES['по умолчанию']

    def create_default_schedule(self, doctor):
        """Создание базового расписания"""
        default_template = self.SCHEDULE_TEMPLATES['по умолчанию']
        for weekday in default_template['weekdays']:
            try:
                Schedule.objects.create(
                    doctor=doctor,
                    weekday=weekday,
                    start_time=default_template['start_time'],
                    end_time=default_template['end_time'],
                    is_active=True
                )
            except Exception as e:
                logger.error(f"Ошибка при создании базового расписания: {str(e)}")






