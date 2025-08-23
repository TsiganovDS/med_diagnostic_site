from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from django.utils import timezone

from config import settings
from users.models import CustomUser
from .models import Appointment, Doctor, Patient, Service, Feedback


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "birth_date", "phone"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop(
            "request", None
        )  # Захватываем request, если он передан
        super().__init__(*args, **kwargs)

        # Если instance передан, заполняем начальные значения
        if kwargs.get("instance"):
            self.fields["first_name"].initial = kwargs["instance"].user.first_name
            self.fields["last_name"].initial = kwargs["instance"].user.last_name


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        initial=timezone.now()
    )

    appointment_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'doctor', 'service', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Оптимизируем запрос к базе данных
        self.fields['service'].queryset = Service.objects.all().select_related('category')

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('appointment_date')
        time = cleaned_data.get('appointment_time')

        if date and time:
            datetime_combined = timezone.make_aware(
                datetime.combine(date, time)
            )
            cleaned_data['datetime'] = datetime_combined

        return cleaned_data


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'equipment_type', 'description']

User = get_user_model()

class DoctorRegistrationForm(UserCreationForm):
    equipment_type = forms.ChoiceField(choices=Doctor.TYPES)
    specialization = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, required=False)
    schedule = forms.CharField(widget=forms.Textarea, required=False)
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = (
            'password1',
            'password2',
            'email',
            'first_name',
            'last_name'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
            doctor = Doctor.objects.create(
                user=user,
                equipment_type=self.cleaned_data['equipment_type'],
                specialization=self.cleaned_data['specialization'],
                description=self.cleaned_data['description'],
                schedule=self.cleaned_data['schedule'],
            )
            doctor.services.set(self.cleaned_data['services'])
            return user


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема сообщения'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ваше сообщение'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Пожалуйста, введите корректный email')
        return email







