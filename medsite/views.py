from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, request
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView

from .models import Patient, Appointment, Doctor
from medsite.forms import PatientForm, AppointmentForm

class HomeView(TemplateView):
    """Контроллер для отображения главной страницы."""
    template_name = 'medsite/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Главная'
        return context_data


class AboutView(TemplateView):
    """Контроллер для отображения страницы о компании."""
    template_name = 'medsite/about_the_company.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'О компании'
        context_data['doctor_count'] = Doctor.objects.count()
        return context_data

class ServicesView(TemplateView):
    """Контроллер для отображения страницы услуги."""
    template_name = 'medsite/services_page.html'

class ContactsView(TemplateView):
    """Контроллер для отображения страницы контакты."""
    template_name = 'medsite/contacts.html'

class SuccessView(TemplateView):
    template_name = 'medsite/appointment_success.html'


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'medsite/appointment_create.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('medsite:appointment_list')

    def form_valid(self, form):
        # Получаем объект формы, но не сохраняем его сразу
        appointment = form.save(commit=False)
        # Устанавливаем пациента из текущего пользователя
        appointment.patient = self.request.user
        # Теперь можно сохранить запись
        appointment.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctors = Doctor.objects.all()
        context['title'] = 'Добавление записи на прием'
        context['doctors'] = doctors
        if doctors.count() == 0:
            context['no_doctor'] = 'Нет доступных врачей!'
        return context


class AppointmentListView(ListView):
    model = Appointment
    context_object_name = 'appointments'
    template_name = 'medsite/appointment_list.html'

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)




class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'medsite/appointments_edit.html'
    success_url = reverse_lazy('medsite:appointment_list')


class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'medsite/appointments_detail.html'
    context_object_name = 'appointment'


class AppointmentDeleteView(DeleteView):
    model = Appointment
    success_url = reverse_lazy('medsite:appointment_list')
    template_name = 'medsite/appointments_delete.html'

