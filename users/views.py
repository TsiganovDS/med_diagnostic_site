from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from medsite.views import GreetingMixin
from .forms import CustomUserCreationForm
from .models import CustomUser


class RegisterView(GreetingMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("medsite:index")

    def form_valid(self, form):
        response = super().form_valid(form)

        send_mail(
            subject="🎉 Добро пожаловать на сайт Медицинской диагностики!",
            message=(
                f"Здравствуйте, {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}!\n\n"
                f"Вы успешно зарегистрировались. "
                f"Если вы не регистрировались, просто проигнорируйте это письмо.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[form.cleaned_data["email"]],
            fail_silently=False,
        )

        return response


class CustomLoginView(GreetingMixin, LoginView):
    model = CustomUser
    template_name = "users/login.html"


class CustomLogoutView(GreetingMixin, LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("medsite:index")


class ProfileView(GreetingMixin, LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Профиль пользователя"
        context["appointments"] = self.object.appointments.all().order_by(
            "appointment_date"
        )
        return context
