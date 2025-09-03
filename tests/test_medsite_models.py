import uuid
from datetime import datetime, time

from django.test import TestCase
from django.utils import timezone

from medsite.models import Appointment, Doctor, Patient, Service, ServiceCategory
from users.models import CustomUser


class TestAppointmentModel(TestCase):
    def setUp(self):
        # Создаем необходимые объекты для тестов
        self.patient = CustomUser.objects.create_user(
            password="testpass", email="patient@example.com"
        )

        # Создаем пользователя для врача
        self.doctor_user = CustomUser.objects.create_user(
            password="testpass", email="doctor@example.com"
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user, first_name="Доктор", last_name="Тест"
        )

        self.service_category = ServiceCategory.objects.create(name="Консультация")

        self.service = Service.objects.create(
            category=self.service_category,
            name="Консультация",
            duration_minutes=30,
            price=100,
            description="Описание",
        )

    def test_create_appointment(self):
        """Тест создания записи"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now().date(),
            appointment_time=timezone.now().time(),
            service=self.service,
            status="pending",
        )

        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.service, self.service)

    def test_get_absolute_url(self):
        """Тест получения URL записи"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            appointment_date=timezone.now().date(),
            appointment_time=timezone.now().time(),
        )

        url = appointment.get_absolute_url()
        self.assertEqual(url, f"/appointment/{appointment.pk}/")

    def test_get_results_link(self):
        """Тест получения ссылки на результаты"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            appointment_date=timezone.now().date(),
            appointment_time=timezone.now().time(),
        )

        # Без файла
        self.assertEqual(appointment.get_results_link(), "Нет результатов")


class TestDoctorModel(TestCase):
    def setUp(self):
        # Создаем пользователя для врача
        self.user = CustomUser.objects.create_user(
            password="testpass", email="doctor@example.com"
        )

    def test_create_doctor(self):
        """Тест создания профиля врача"""
        doctor = Doctor.objects.create(
            user=self.user,
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            equipment_type="узи",
            specialization="Терапевт",
            description="Опытный врач",
        )

        self.assertEqual(doctor.user, self.user)
        self.assertEqual(doctor.first_name, "Иван")
        self.assertEqual(doctor.last_name, "Иванов")
        self.assertEqual(doctor.middle_name, "Иванович")
        self.assertEqual(doctor.equipment_type, "узи")
        self.assertEqual(doctor.specialization, "Терапевт")
        self.assertEqual(doctor.description, "Опытный врач")
        self.assertTrue(doctor.is_active)

    def test_str_method(self):
        """Тест метода __str__"""
        # Создаем нового пользователя для этого теста
        user = CustomUser.objects.create_user(
            password="testpass", email="doctor2@example.com"
        )

        doctor = Doctor.objects.create(
            user=user, first_name="Иван", last_name="Иванов", middle_name="Иванович"
        )
        self.assertEqual(str(doctor), "Иванов Иван Иванович")

    def test_is_active(self):
        """Тест статуса активности врача"""
        # Создаем активного врача с новым пользователем
        user_active = CustomUser.objects.create_user(
            password="testpass", email="active@example.com"
        )

        active_doctor = Doctor.objects.create(
            user=user_active,
            first_name="Активный",
            last_name="Доктор",
            middle_name="Тест",
            is_active=True,
        )
        self.assertTrue(active_doctor.is_active)

        # Создаем неактивного врача с новым пользователем
        user_inactive = CustomUser.objects.create_user(
            password="testpass", email="inactive@example.com"
        )

        inactive_doctor = Doctor.objects.create(
            user=user_inactive,
            first_name="Неактивный",
            last_name="Доктор",
            middle_name="Тест",
            is_active=False,
        )
        self.assertFalse(inactive_doctor.is_active)


class TestAppointmentStrMethod(TestCase):
    def setUp(self):
        # Генерируем уникальные email адреса
        patient_email = f"patient_{uuid.uuid4()}@example.com"
        doctor_email = f"doctor_{uuid.uuid4()}@example.com"

        # Создаем тестовых пользователей
        self.patient_user = CustomUser.objects.create(
            email=patient_email, first_name="Пациент", last_name="Иванович"
        )
        self.doctor_user = CustomUser.objects.create(
            email=doctor_email, first_name="Доктор", last_name="Петрович"
        )

        # Создаем профили пациентов и врачей
        self.patient = Patient.objects.create(user=self.patient_user)
        self.doctor = Doctor.objects.create(user=self.doctor_user)

        # Создаем запись, используя правильные типы данных
        self.appointment = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            appointment_date=timezone.now().date(),
            appointment_time=time(14, 30),
        )

    def test_full_info(self):
        expected_str = (
            f"Запись Пациент Иванович к  на "
            f"{datetime.combine(self.appointment.appointment_date,
                                self.appointment.appointment_time).strftime('%d.%m.%Y %H:%M')}"
        )
        self.assertEqual(str(self.appointment), expected_str)

    def test_no_doctor(self):
        self.appointment.doctor = None
        self.appointment.save()
        expected_str = (
            f"Запись Пациент Иванович к Неизвестно на "
            f"{datetime.combine(self.appointment.appointment_date,
                                self.appointment.appointment_time).strftime('%d.%m.%Y %H:%M')}"
        )
        self.assertEqual(str(self.appointment), expected_str)

    def test_only_time(self):
        expected_str = (
            f"Запись Пациент Иванович к  на 03.09.2025 "
            f"{self.appointment.appointment_time.strftime('%H:%M')}"
        )
        self.assertEqual(str(self.appointment), expected_str)
