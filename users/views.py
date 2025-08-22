from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.forms import inlineformset_factory
from django.http import request
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, DetailView, UpdateView

from medsite.forms import AppointmentForm, PatientForm
from medsite.models import Appointment, Patient

from .forms import CustomUserCreationForm
from .models import CustomUser


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("medsite:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        print("Пробую отправить письмо на:", form.cleaned_data["email"])
        print("SMTP USER:", repr(settings.EMAIL_HOST_USER))
        print("SMTP PASS:", repr(settings.EMAIL_HOST_PASSWORD))

        send_mail(
            subject="🎉 Добро пожаловать на сайт Медицинской диагностики!",
            message=(
                f"Здравствуйте, {form.cleaned_data['last_name']} {form.cleaned_data['first_name']}!\n\n"
                f"Вы успешно зарегистрировались. "
                f"Если вы не регистрировались, просто проигнорируйте это письмо.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[form.cleaned_data["email"]],
            fail_silently=False,
        )

        return response


class CustomLoginView(LoginView):
    model = CustomUser
    template_name = "users/login.html"


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("medsite:index")


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Профиль пользователя"
        context["appointments"] = self.object.appointments.all().order_by("appointment_date")
        return context


class PatientProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = "users/update_profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        # Получаем или создаем профиль пациента
        patient, created = Patient.objects.get_or_create(user=self.request.user)
        return patient

    def form_valid(self, form):
        response = super().form_valid(form)

        # Обновляем информацию в CustomUser
        user = self.request.user
        user.first_name = form.cleaned_data.get("first_name", user.first_name)
        user.last_name = form.cleaned_data.get("last_name", user.last_name)
        user.save()

        messages.success(self.request, "Ваш профиль успешно обновлён.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при обновлении профиля.")
        return super().form_invalid(form)
