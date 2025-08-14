from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from .models import Patient, Appointment
from medsite.forms import PatientForm, AppointmentForm

class HomeView(TemplateView):
    template_name = 'medsite/index.html'

class AboutView(TemplateView):
    template_name = 'medsite/about_the_company.html'

class ServicesView(TemplateView):
    template_name = 'medsite/services_page.html'

class ContactsView(TemplateView):
    template_name = 'medsite/contacts.html'

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patient_list.html', {'patients': patients})


def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})


def appointment_list(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    appointments = Appointment.objects.filter(patient=patient)
    return render(request, 'appointment_list.html', {'patient': patient, 'appointments': appointments})


def add_appointment(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            return redirect('appointment_list', patient_id=patient.id)
    else:
        form = AppointmentForm()
    return render(request, 'register.html', {'form': form, 'patient': patient})
