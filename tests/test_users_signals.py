from django.contrib.auth import get_user_model
from django.test import TestCase

from medsite.models import Patient


class PatientSignalTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_patient_not_created_on_user_update(self):
        # Создаем пользователя
        user = self.User.objects.create(
            email="test@example.com",
            password="testpass123",
        )

        # Сохраняем пациента
        initial_patient_count = Patient.objects.count()

        # Обновляем пользователя
        user.first_name = "New Name"
        user.save()

        # Проверяем, что количество пациентов не изменилось
        self.assertEqual(Patient.objects.count(), initial_patient_count)

    def test_patient_not_created_for_existing_user(self):
        # Создаем пользователя
        user = self.User.objects.create(
            email="test@example.com",
            password="testpass123",
        )

        # Сохраняем пациента
        initial_patient_count = Patient.objects.count()

        # Повторно сохраняем пользователя
        user.save()

        # Проверяем, что количество пациентов не изменилось
        self.assertEqual(Patient.objects.count(), initial_patient_count)

    def test_patient_unique_per_user(self):
        # Создаем пользователя
        user = self.User.objects.create(
            email="test@example.com",
            password="testpass123",
        )

        # Пытаемся создать пациента вручную
        Patient.objects.create(user=user)

        # Проверяем, что количество пациентов остается 1
        self.assertEqual(Patient.objects.filter(user=user).count(), 1)
