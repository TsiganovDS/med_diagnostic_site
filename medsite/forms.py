from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from users.models import CustomUser
from medsite.models import Appointment, Diagnosis, Doctor, Feedback, Patient, Service

User = get_user_model()


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "birth_day", "phone"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop(
            "request", None
        )  # Захватываем request, если он передан
        super().__init__(*args, **kwargs)

        # Если instance передан, заполняем начальные значения
        if kwargs.get("instance"):
            self.fields["first_name"].initial = kwargs["instance"].user.first_name
            self.fields["last_name"].initial = kwargs["instance"].user.last_name
            self.fields["birth_day"].initial = kwargs["instance"].user.birth_day
            self.fields["phone"].initial = kwargs["instance"].user.phone


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "patient",
            "doctor",
            "service",
            "appointment_date",
            "appointment_time",
            "reason",
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "appointment_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "appointment_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "patient": forms.Select(attrs={"class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "service": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "reason": "Причина обращения",
            "appointment_date": "Дата приема",
            "appointment_time": "Время приема",
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            if self.request.user.is_staff:
                self.fields["patient"].queryset = CustomUser.objects.filter(
                    user_type="patient"
                )
            else:
                self.fields["patient"].initial = self.request.user
                self.fields["patient"].disabled = True

        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True).order_by(
            "last_name"
        )
        self.fields["service"].queryset = Service.objects.select_related("category")

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("appointment_date")
        time = cleaned_data.get("appointment_time")

        if date and time:
            datetime_combined = timezone.make_aware(datetime.combine(date, time))
            if datetime_combined < timezone.now():
                raise ValidationError("Время записи должно быть в будущем")

            cleaned_data["datetime"] = datetime_combined
        return cleaned_data


class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "appointment_date", "appointment_time"]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time"}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["specialization", "equipment_type", "description"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["user"].queryset = User.objects.filter(user_type="doctor")


class DoctorRegistrationForm(UserCreationForm):
    equipment_type = forms.ChoiceField(choices=Doctor.TYPES)
    specialization = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, required=False)
    schedule = forms.CharField(widget=forms.Textarea, required=False)
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = ("password1", "password2", "email", "first_name", "last_name")

    def save(self, commit=True):

        from medsite.models import Doctor

        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
            doctor = Doctor.objects.create(
                user=user,
                equipment_type=self.cleaned_data["equipment_type"],
                specialization=self.cleaned_data["specialization"],
                description=self.cleaned_data["description"],
                schedule=self.cleaned_data["schedule"],
            )
            doctor.services.set(self.cleaned_data["services"])
            return user


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите ваше имя"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Введите email"}
            ),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Тема сообщения"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Ваше сообщение",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Пожалуйста, введите корректный email")
        return email

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ["appointment", "diagnosis_date", "description"]


    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.initial["patient"] = user.pk
            self.fields["appointment"].queryset = Appointment.objects.filter(
                patient=user
            )
