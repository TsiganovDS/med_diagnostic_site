from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import DateInput

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    birth_day = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    phone = forms.CharField(
        max_length=15,
        required=False
    )
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'birth_day')
        widgets = {
            'birth_day': DateInput(attrs={'type': 'date'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'birth_day')
