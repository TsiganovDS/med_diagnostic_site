from datetime import datetime


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, request
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from medsite.forms import AppointmentForm, DoctorForm, DoctorRegistrationForm

from .models import Appointment, Doctor


class HomeView(TemplateView):
    """Контроллер для отображения главной страницы."""

    template_name = "medsite/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = "Главная"
        return context_data


class AboutView(TemplateView):
    """Контроллер для отображения страницы о компании."""

    template_name = "medsite/about_the_company.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = "О компании"
        context_data["doctor_count"] = Doctor.objects.count()
        return context_data


class ServicesView(TemplateView):
    """Контроллер для отображения страницы услуги."""

    template_name = "medsite/services_page.html"


class ContactsView(TemplateView):
    """Контроллер для отображения страницы контакты."""

    template_name = "medsite/contacts.html"


class SuccessView(TemplateView):
    template_name = "medsite/appointment_success.html"


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'medsite/appointment_form.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('users:profile')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Отображаем пустую форму при GET-запросе
        form = AppointmentForm()
        return render(request, 'medsite/appointment_form.html', {'form': form})

    def form_valid(self, form):
        try:
            # Получаем очищенные данные
            cleaned_data = form.cleaned_data

            # Конвертируем дату и время в timezone-aware формат
            appointment_datetime = timezone.make_aware(
                datetime.combine(
                    cleaned_data['appointment_date'],
                    cleaned_data['appointment_time']
                )
            )

            # Проверяем занятость времени
            if Appointment.objects.filter(
                    doctor=cleaned_data['doctor'],
                    appointment_date=appointment_datetime.date(),
                    appointment_time=appointment_datetime.time()
            ).exists():
                messages.error(self.request, 'Это время уже занято другим пациентом')
                return self.get(self.request)

            # Сохраняем запись
            appointment = form.save(commit=False)
            appointment.patient = self.request.user
            appointment.save()

            messages.success(self.request, 'Запись успешно создана!')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка при сохранении: {str(e)}')
            return self.get(self.request)

    def form_invalid(self, form):
        messages.error(self.request, 'Форма содержит ошибки')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context






class AppointmentListView(ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "medsite/appointment_list.html"

    def get_queryset(self):
        # Используем get_queryset вместо переопределения get()
        return Appointment.objects.filter(
            patient=self.request.user
        ).order_by('appointment_date', 'appointment_time')

class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "medsite/appointments_edit.html"
    success_url = reverse_lazy("users:profile")


class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = "medsite/appointments_detail.html"
    context_object_name = "appointment"


class AppointmentDeleteView(DeleteView):
    model = Appointment
    success_url = reverse_lazy("users:profile")
    template_name = "medsite/appointments_delete.html"


class DoctorListView(LoginRequiredMixin, generic.ListView):
    model = Doctor
    template_name = 'medsite/doctors_list.html'
    context_object_name = 'doctors'
    paginate_by = 10


class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'medsite/doctor_update.html'
    success_url = '/doctors/'

    def test_func(self):
        return self.request.user.is_staff


class DoctorRegistrationView(generic.CreateView):
    form_class = DoctorRegistrationForm
    template_name = 'medsite/doctor_register.html'
    success_url = reverse_lazy('login')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
