from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from medsite.models import Appointment
from users.forms import CustomUserCreationForm
from users.models import CustomUser


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("users:register")

    def test_get_request(self):
        """Тест GET-запроса"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_valid_registration(self):
        """Тест успешной регистрации"""
        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "username": "ivanov",
            "password1": "strongpass123",
            "password2": "strongpass123",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("medsite:index"))

        # Проверяем создание пользователя
        user = CustomUser.objects.get(email="ivan@example.com")
        self.assertEqual(user.first_name, "Иван")
        self.assertEqual(user.last_name, "Иванов")

    def test_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        # Создаем пользователя
        CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Тестовый",
            last_name="Пользователь",
        )

        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "test@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        # Правильно проверяем ошибку email
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("email", form.errors)
        self.assertIn(
            "Custom user с таким E-mail уже существует.", form.errors["email"][0]
        )


class TestProfileView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            password="testpass123",
            email="test@example.com",
            first_name="Тестовый",
            last_name="Пользователь",
        )
        self.appointment1 = Appointment.objects.create(
            patient=self.user, appointment_date=timezone.now(), appointment_time="10:00"
        )
        self.appointment2 = Appointment.objects.create(
            patient=self.user,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
            appointment_time="11:00",
        )

    def test_profile_view_anonymous(self):
        """Тест доступа к профилю для неавторизованного пользователя"""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
        self.assertIn("/login/", response.url)

    def test_profile_view_authenticated(self):
        """Тест доступа к профилю для авторизованного пользователя"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertEqual(response.context["user_profile"], self.user)
        self.assertEqual(response.context["title"], "Профиль пользователя")

    def test_appointments_in_context(self):
        """Тест передачи записей в контекст"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(
            list(response.context["appointments"]),
            [self.appointment1, self.appointment2],
        )

    def test_appointments_ordering(self):
        """Тест сортировки записей по дате"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        appointments = response.context["appointments"]
        self.assertEqual(
            list(appointments), [self.appointment1, self.appointment2]
        )  # Проверяем порядок сортировки

    def test_profile_view_with_no_appointments(self):
        """Тест профиля без записей"""
        # Удаляем записи
        Appointment.objects.all().delete()

        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["appointments"]), [])

    def test_profile_view_with_multiple_appointments(self):
        """Тест профиля с несколькими записями"""
        # Создаем дополнительные записи
        Appointment.objects.create(
            patient=self.user,
            appointment_date=timezone.now() + timezone.timedelta(days=2),
            appointment_time="12:00",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["appointments"].count(), 3)
