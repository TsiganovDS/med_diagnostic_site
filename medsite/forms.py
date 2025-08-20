from django import forms
from .models import Appointment, Patient, Doctor


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'birth_date', 'phone']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Захватываем request, если он передан
        super().__init__(*args, **kwargs)

        # Если instance передан, заполняем начальные значения
        if kwargs.get('instance'):
            self.fields['first_name'].initial = kwargs['instance'].user.first_name
            self.fields['last_name'].initial = kwargs['instance'].user.last_name



class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальные значения или добавляем дополнительные фильтры
        self.fields['doctor'].queryset = Doctor.objects.all()
