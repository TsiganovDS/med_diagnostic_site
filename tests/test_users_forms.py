from django.test import TestCase
from django.utils import timezone

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser


class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        data = {
            "email": "test@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+79991234567",
            "birth_day": timezone.now().date(),
        }
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = {
            "email": "invalid-email",
            "password1": "strongpass123",
            "password2": "strongpass123",
            "first_name": "John",
            "last_name": "Doe",
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch(self):
        data = {
            "email": "test@example.com",
            "password1": "strongpass123",
            "password2": "wrongpass123",
            "first_name": "John",
            "last_name": "Doe",
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_optional_fields(self):
        data = {
            "email": "test@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
            "first_name": "John",
            "last_name": "Doe",
        }
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_format(self):
        data = {
            "email": "test@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890123456",
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)


class CustomUserChangeFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

    def test_valid_form(self):
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+79991234567",
            "birth_day": timezone.now().date(),
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = {
            "email": "invalid-email",
            "first_name": "John",
            "last_name": "Doe",
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_optional_fields(self):
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_format(self):
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890123456",
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_birth_day_validation(self):
        # Проверка корректной даты
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "birth_day": "2000-01-01",
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertTrue(form.is_valid())

        # Проверка некорректной даты
        data["birth_day"] = "31-02-2000"
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("birth_day", form.errors)

    def test_saving_form(self):
        data = {
            "email": "newemail@example.com",
            "first_name": "NewFirstName",
            "last_name": "NewLastName",
            "phone": "+79991234567",
            "birth_day": timezone.now().date(),
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        if form.is_valid():
            form.save()
            self.user.refresh_from_db()
            self.assertEqual(self.user.email, data["email"])
            self.assertEqual(self.user.first_name, data["first_name"])
            self.assertEqual(self.user.last_name, data["last_name"])
            self.assertEqual(self.user.phone, data["phone"])
            self.assertEqual(self.user.birth_day, data["birth_day"])
