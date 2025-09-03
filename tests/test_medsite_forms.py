from django.contrib.auth import get_user_model
from django.test import TestCase

from medsite.forms import DoctorRegistrationForm
from medsite.models import Doctor, Service, ServiceCategory


class TestDoctorRegistrationFormTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.service_category = ServiceCategory.objects.create(name="Консультация")
        self.service = Service.objects.create(
            category=self.service_category,
            name="Консультация",
            duration_minutes=30,
            price=100,
            description="Описание",
        )

    def test_invalid_password(self):
        form_data = {
            "password1": "weak",
            "password2": "weak",
            "email": "doctor@example.com",
            "first_name": "Иван",
            "last_name": "Иванов",
            "equipment_type": Doctor.TYPES[0][0],
            "specialization": "Терапевт",
        }

        form = DoctorRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_missing_required_fields(self):
        form_data = {
            "password1": "strongpass123!",
            "password2": "strongpass123!",
            "email": "doctor@example.com",
            "first_name": "Иван",
            "last_name": "Иванов",
        }

        form = DoctorRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("equipment_type", form.errors)
        self.assertIn("specialization", form.errors)

    def test_unique_email(self):
        existing_user = self.User.objects.create_user(
            email="existing@example.com", password="password123"
        )

        form_data = {
            "password1": "strongpass123!",
            "password2": "strongpass123!",
            "email": existing_user.email,
            "first_name": "Иван",
            "last_name": "Иванов",
            "equipment_type": Doctor.TYPES[0][0],
            "specialization": "Терапевт",
        }

        form = DoctorRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
