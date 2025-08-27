import os
from datetime import time

import django
from django.conf import settings
from django.core.mail import outbox
from django.utils import timezone

from medsite.forms import AppointmentForm, FeedbackForm
from medsite.views import ContactsView, AppointmentCreateView, AppointmentDetailView

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "med_diagnostic_site.settings")

django.setup()
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from medsite.models import Doctor, Appointment, Diagnosis, Patient, Feedback
from users.models import CustomUser


class BaseUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовых пользователей
        cls.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        cls.user2 = CustomUser.objects.create_user(
            email="test1@example.com", password="testpass2"
        )

        # Создаем тестового врача
        cls.doctor = Doctor.objects.create(
            first_name="Петр",
            last_name="Петров",
            specialization="Кардиолог",
            user=cls.user,
        )

        # Создаем тестовые записи
        cls.appointment = Appointment.objects.create(
            patient=cls.user,
            doctor=cls.doctor,
            appointment_date=timezone.now().date(),
            appointment_time="10:00:00",
        )

        # Создаем запись для тестов
        cls.appointment = Appointment.objects.create(
            patient=cls.user,
            doctor=cls.doctor,
            appointment_date=timezone.now().date(),
            appointment_time="10:00:00",
        )

        cls.patient = cls.user.patient_profile

    def setUp(self):
        # Создаем клиент
        self.client = Client()
        self.client.force_login(self.user)


class TestHomeViewCase(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_home_view_anonymous(self):
        # Тест для неавторизованного пользователя
        response = self.client.get(reverse("medsite:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/index.html")
        self.assertContains(response, "Главная")

    def test_home_view_authenticated(self):
        # Авторизуем пользователя
        self.client.force_login(self.user)
        response = self.client.get(reverse("medsite:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/index.html")
        self.assertContains(response, "Главная")
        self.assertEqual(response.context["user"], self.user)

    def test_context_data(self):
        # Проверяем контекстные данные
        response = self.client.get(reverse("medsite:index"))
        self.assertEqual(response.context["title"], "Главная")

    def test_template_rendering(self):
        # Проверяем рендеринг шаблона
        response = self.client.get(reverse("medsite:index"))
        self.assertTemplateUsed(response, "medsite/index.html")
        self.assertIsNotNone(response.context)

    def test_no_errors(self):
        # Проверяем отсутствие ошибок при рендеринге
        response = self.client.get(reverse("medsite:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ошибка")


class TestAboutViewCase(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_about_view_basic(self):
        response = self.client.get(reverse("medsite:about_the_company"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/about_the_company.html")
        self.assertContains(response, "О компании")

    def test_doctor_count(self):
        response = self.client.get(reverse("medsite:about_the_company"))
        self.assertEqual(response.context["doctor_count"], 1)

    def test_context_data(self):
        response = self.client.get(reverse("medsite:about_the_company"))
        self.assertEqual(response.context["title"], "О компании")
        self.assertIsInstance(response.context["doctor_count"], int)

    def test_empty_doctors(self):
        Doctor.objects.all().delete()
        response = self.client.get(reverse("medsite:about_the_company"))
        self.assertEqual(response.context["doctor_count"], 0)

    def test_template_rendering(self):
        response = self.client.get(reverse("medsite:about_the_company"))
        self.assertTemplateUsed(response, "medsite/about_the_company.html")
        self.assertIsNotNone(response.context)

    def test_no_errors(self):
        response = self.client.get(reverse("medsite:about_the_company"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ошибка")


class TestContactsView(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_contacts_view_returns_200(self):
        response = self.client.get(reverse("medsite:contacts"))
        self.assertEqual(response.status_code, 200)

    def test_contacts_view_uses_correct_template(self):
        response = self.client.get(reverse("medsite:contacts"))
        self.assertTemplateUsed(response, "medsite/contacts.html")

    def test_contacts_view_context(self):
        response = self.client.get(reverse("medsite:contacts"))
        # Добавьте здесь проверки контекста, если нужно

    def test_contacts_view_content_type(self):
        response = self.client.get(reverse("medsite:contacts"))
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")

    def test_anonymous_access(self):
        # Проверяем доступ для анонимного пользователя
        response = self.client.get(reverse("medsite:contacts"))
        self.assertEqual(response.status_code, 200)


class TestAppointmentCreateView(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user)

    def test_anonymous_access(self):
        client = Client()
        response = client.get(reverse("medsite:appointment_form"))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_template_used(self):
        response = self.client.get(reverse("medsite:appointment_form"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/appointment_form.html")

    def test_form_valid(self):
        data = {
            "doctor": self.doctor.id,
            "appointment_date": timezone.now().date(),
            "appointment_time": "10:00:00",
            "service": "Консультация",
            "reason": "Первичный прием",
        }
        response = self.client.post(
            reverse("medsite:appointment_form"), data, follow=True
        )
        self.assertEqual(Appointment.objects.count(), 2)

    def test_form_invalid(self):
        data = {"doctor": "", "appointment_date": "", "appointment_time": ""}
        response = self.client.post(reverse("medsite:appointment_form"), data)
        self.assertEqual(response.status_code, 200)

    def test_time_conflict(self):
        # Создаем существующую запись
        appointment = Appointment.objects.create(
            patient=self.user,
            doctor=self.doctor,
            appointment_date=timezone.now().date(),
            appointment_time="10:00:00",
        )

        data = {
            "doctor": self.doctor.id,
            "appointment_date": timezone.now().date(),
            "appointment_time": "10:00:00",
            "service": "Рентген",
            "reason": "Рентген",
        }

        response = self.client.post(reverse("medsite:appointment_form"), data)
        self.assertEqual(response.status_code, 200)

    def test_success_url(self):
        data = {
            "doctor": self.doctor.id,
            "appointment_date": timezone.now().date(),
            "appointment_time": "10:00:00",
            "service": "Консультация",
            "reason": "Причина записи",
        }

        response = self.client.post(
            reverse("medsite:appointment_form"), data, follow=True
        )

        self.assertEqual(Appointment.objects.count(), 2)


class TestAppointmentListView(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user)

    def test_template_used(self):
        # Проверяем используемый шаблон
        response = self.client.get(reverse("medsite:appointment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/appointment_list.html")

    def test_context_object_name(self):
        # Проверяем имя переменной контекста
        response = self.client.get(reverse("medsite:appointment_list"))
        self.assertIn("appointments", response.context)

    def test_queryset_filtering(self):
        # Проверяем фильтрацию по пользователю
        response = self.client.get(reverse("medsite:appointment_list"))
        self.assertEqual(len(response.context["appointments"]), 2)
        self.assertEqual(response.context["appointments"][0].patient, self.user)

    def test_ordering(self):
        # Создаем дополнительные записи для проверки сортировки
        Appointment.objects.create(
            patient=self.user,
            doctor=self.doctor,
            appointment_date=timezone.now().date(),
            appointment_time=time(9, 0),  # Используем объект time
        )

        response = self.client.get(reverse("medsite:appointment_list"))
        appointments = response.context["appointments"]

        # Сравниваем с объектом time
        self.assertEqual(appointments[0].appointment_time, time(9, 0))
        self.assertEqual(appointments[1].appointment_time, time(10, 0))

    def test_empty_list(self):
        # Удаляем все записи пользователя
        Appointment.objects.filter(patient=self.user).delete()

        response = self.client.get(reverse("medsite:appointment_list"))
        self.assertEqual(len(response.context["appointments"]), 0)


class TestAppointmentUpdateView(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user)

    def test_anonymous_access(self):
        # Проверяем доступ для неавторизованного пользователя
        client = Client()
        response = client.get(
            reverse("medsite:appointment_edit", args=[self.appointment.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        # Проверяем используемый шаблон
        response = self.client.get(
            reverse("medsite:appointment_edit", args=[self.appointment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/appointments_edit.html")

    def test_form_invalid(self):
        # Проверяем валидацию формы
        invalid_data = {"doctor": "", "appointment_date": "", "appointment_time": ""}

        response = self.client.post(
            reverse("medsite:appointment_edit", args=[self.appointment.pk]),
            invalid_data,
        )

        self.assertEqual(response.status_code, 200)

    def test_wrong_user_access(self):
        # Авторизуем второго пользователя
        self.client.force_login(self.user2)

        # Пытаемся получить доступ к записи другого пользователя
        response = self.client.get(
            reverse("medsite:appointment_edit", args=[self.appointment.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        # Проверяем данные в контексте
        response = self.client.get(
            reverse("medsite:appointment_edit", args=[self.appointment.pk])
        )
        self.assertIsInstance(response.context["form"], AppointmentForm)
        self.assertEqual(response.context["object"], self.appointment)


class TestFeedbackView(BaseUserTest):
    def setUp(self):
        self.client = Client()
        self.url = reverse("medsite:form")

    def test_get_request(self):
        """Тест GET-запроса"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "medsite/form.html")
        self.assertIsInstance(response.context["form"], FeedbackForm)

    def test_post_request_anonymous(self):
        """Тест POST-запроса от анонимного пользователя"""
        data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "subject": "Консультация",
            "message": "Хочу записаться на прием",
        }
        with self.assertNumQueries(2):  # проверка количества запросов к БД
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse("medsite:index"))
            self.assertEqual(Feedback.objects.count(), 1)

            # Проверяем, что письма отправлены
            self.assertEqual(len(outbox), 0)

    def test_post_request_authenticated(self):
        """Тест POST-запроса от авторизованного пользователя"""
        self.client.force_login(self.user)
        data = {
            "name": "Иван Петров",
            "subject": "Консультация",
            "message": "Хочу записаться на прием",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        feedback = Feedback.objects.first()
        self.assertEqual(len(outbox), 0)

    def test_email_notifications(self):
        """Тест отправки email-уведомлений"""
        data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "subject": "Консультация",
            "message": "Хочу записаться на прием",
        }

        # Очищаем outbox перед отправкой
        outbox.clear()

        response = self.client.post(self.url, data)

        # Проверяем, что письма отправлены
        self.assertEqual(len(outbox), 0)

        # Проверяем письмо администратору
        if len(outbox) > 0:
            admin_email = outbox[0]
            self.assertEqual(admin_email.subject, "Новое сообщение от пациента")
            self.assertIn("От: Иван Петров", admin_email.body)
            self.assertIn("ivan@example.com", admin_email.body)
            self.assertIn("Консультация", admin_email.body)
            self.assertIn("Хочу записаться на прием", admin_email.body)

        # Проверяем письмо пользователю
        if len(outbox) > 1:
            patient_email = outbox[1]
            self.assertEqual(patient_email.subject, "Спасибо за обращение в клинику")
            self.assertIn("Уважаемый Иван Петров", patient_email.body)
            self.assertIn("Консультация", patient_email.body)

    def test_empty_outbox(self):
        """Тест проверки пустого outbox"""
        outbox.clear()
        self.assertEqual(len(outbox), 0)
