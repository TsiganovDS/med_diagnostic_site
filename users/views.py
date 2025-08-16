from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

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
                f"Здравствуйте, {form.cleaned_data['username']}!\n\n"
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


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("medsite:index")


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile.html"

    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ["username", "email"]
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user
