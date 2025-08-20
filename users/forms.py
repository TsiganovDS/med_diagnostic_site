from django import forms
from django.contrib.auth.forms import UserCreationForm


from medsite.models import Patient
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Данный номер телефона уже занят!")
        return phone

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'birth_day', 'password1', 'password2')



    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создание профиля пациента
            Patient.objects.create(user=user)
        return user


