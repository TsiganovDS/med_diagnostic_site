from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.core.mail import send_mail
from django.forms import inlineformset_factory
from django.http import request
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, DetailView, UpdateView

from medsite.forms import PatientForm, AppointmentForm
from medsite.models import Patient, Appointment
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
                f"Здравствуйте, {form.cleaned_data['last_name' 'first_name']}!\n\n"
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

    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        context_data = self.get_context_data()
        formset = context_data['formset']
        if formset.is_valid() and form.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(formset=formset, form=form))


class PatientProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'users/update_profile.html'
    success_url = reverse_lazy('medsite:appointment_list')

    def get_object(self, queryset=None):
        # Получаем или создаем профиль пациента
        patient, created = Patient.objects.get_or_create(user=self.request.user)
        return patient

    def form_valid(self, form):
        response = super().form_valid(form)

        # Обновляем информацию в CustomUser
        user = self.request.user
        user.first_name = form.cleaned_data.get('first_name', user.first_name)
        user.last_name = form.cleaned_data.get('last_name', user.last_name)
        user.save()

        messages.success(self.request, 'Ваш профиль успешно обновлён.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при обновлении профиля.')
        return super().form_invalid(form)




