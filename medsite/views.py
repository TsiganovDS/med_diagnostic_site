from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View, generic
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from config import settings
from config.settings import ADMIN_EMAIL_LIST
from medsite.forms import (
    AppointmentForm,
    DiagnosisForm,
    DoctorForm,
    DoctorRegistrationForm,
    FeedbackForm,
    PatientForm,
)

from .models import Appointment, Diagnosis, Doctor, Patient


class GreetingMixin:
    def get_time_of_day_greeting(self):
        current_time = timezone.localtime()
        current_hour = current_time.hour
        if current_hour < 12:
            return "Доброе утро"
        elif 12 <= current_hour < 18:
            return "Добрый день"
        elif 18 <= current_hour < 00:
            return "Добрый вечер"
        else:
            return "Доброй ночи"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["greeting"] = self.get_time_of_day_greeting()
        return context


class HomeView(GreetingMixin, TemplateView):
    template_name = "medsite/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная"

        if self.request.user.is_authenticated:
            context["user"] = self.request.user

        return context


class AboutView(GreetingMixin, TemplateView):
    """Контроллер для отображения страницы о компании."""

    template_name = "medsite/about_the_company.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = "О компании"
        context_data["doctor_count"] = Doctor.objects.count()
        return context_data


class ServicesView(GreetingMixin, TemplateView):
    """Контроллер для отображения страницы услуги."""

    template_name = "medsite/services_page.html"


class ContactsView(GreetingMixin, TemplateView):
    """Контроллер для отображения страницы контакты."""

    template_name = "medsite/contacts.html"


class SuccessView(GreetingMixin, TemplateView):
    template_name = "medsite/appointment_success.html"


class AppointmentCreateView(GreetingMixin, LoginRequiredMixin, CreateView):
    template_name = "medsite/appointment_form.html"
    form_class = AppointmentForm
    success_url = reverse_lazy("users:profile")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Отображаем пустую форму при GET-запросе
        form = AppointmentForm()
        return render(request, "medsite/appointment_form.html", {"form": form})

    def form_valid(self, form):
        try:
            # Получаем очищенные данные
            cleaned_data = form.cleaned_data

            # Конвертируем дату и время в timezone-aware формат
            appointment_datetime = timezone.make_aware(
                datetime.combine(
                    cleaned_data["appointment_date"], cleaned_data["appointment_time"]
                )
            )

            # Проверяем занятость времени
            if Appointment.objects.filter(
                doctor=cleaned_data["doctor"],
                appointment_date=appointment_datetime.date(),
                appointment_time=appointment_datetime.time(),
            ).exists():
                messages.error(self.request, "Это время уже занято другим пациентом")
                return super().form_invalid(form)  # Возвращаем форму с ошибкой

            # Сохраняем запись
            appointment = form.save(commit=False)
            appointment.patient = self.request.user
            appointment.save()

            messages.success(self.request, "Запись успешно создана!")
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Произошла ошибка при сохранении: {str(e)}")
            return super().form_invalid(form)


class AppointmentListView(GreetingMixin, ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "medsite/appointment_list.html"

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user).order_by(
            "appointment_date", "appointment_time"
        )


class AppointmentUpdateView(GreetingMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "medsite/appointments_edit.html"
    success_url = reverse_lazy("users:profile")


class AppointmentDetailView(GreetingMixin, DetailView):
    model = Appointment
    template_name = "medsite/appointments_detail.html"
    context_object_name = "appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["diagnosis"] = self.object.diagnosis
        except Diagnosis.DoesNotExist:
            context["diagnosis"] = None
        return context


class AppointmentDeleteView(GreetingMixin, DeleteView):
    model = Appointment
    success_url = reverse_lazy("users:profile")
    template_name = "medsite/appointments_delete.html"


class DoctorListView(GreetingMixin, LoginRequiredMixin, generic.ListView):
    model = Doctor
    template_name = "medsite/doctors_list.html"
    context_object_name = "doctors"
    paginate_by = 10


class DoctorUpdateView(
    GreetingMixin, LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Doctor
    form_class = DoctorForm
    template_name = "medsite/doctor_update.html"
    success_url = reverse_lazy("doctor_list")

    def test_func(self):
        return self.request.user.is_staff


class DoctorRegistrationView(GreetingMixin, generic.CreateView):
    form_class = DoctorRegistrationForm
    template_name = "medsite/doctor_register.html"
    success_url = reverse_lazy("medsite:index")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FeedbackView(GreetingMixin, View):
    template_name = "medsite/form.html"

    form_class = FeedbackForm
    success_url = reverse_lazy("medsite:index")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, "medsite/form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        try:
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()

            self.send_notification_email(feedback)
            return redirect("medsite:index")

        except Exception:
            return JsonResponse(
                {"success": False, "message": "Произошла ошибка при обработке запроса"}
            )

    def send_notification_email(self, feedback):
        # Проверяем настройки email в settings
        if not settings.EMAIL_HOST or not settings.EMAIL_HOST_USER:
            raise Exception("Не настроены параметры email в settings.py")

        # Сообщение для администраторов
        admin_recipients = getattr(
            settings, ADMIN_EMAIL_LIST, ["dm.tsiganov@icloud.com"]
        )
        if not isinstance(admin_recipients, list):
            admin_recipients = admin_recipients

        admin_email = EmailMultiAlternatives(
            "Новое сообщение от пациента",
            f"От: {feedback.name} ({feedback.email})\n"
            f"Тема: {feedback.subject}\n\n"
            f"Сообщение: {feedback.message}",
            settings.DEFAULT_FROM_EMAIL,
            admin_recipients,
        )
        admin_email.send()

        # Сообщение для пациента
        if feedback.email:
            patient_email = EmailMultiAlternatives(
                "Спасибо за обращение в клинику",
                f"Уважаемый {feedback.name},\n\n"
                f"Благодарим вас за обращение в нашу клинику.\n"
                f"Мы получили ваше сообщение по теме: {feedback.subject}\n\n"
                f"Наш специалист свяжется с вами в ближайшее время.",
                settings.DEFAULT_FROM_EMAIL,
                [feedback.email],
            )
            patient_email.send()


class PatientProfileUpdateView(GreetingMixin, LoginRequiredMixin, generic.UpdateView):
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
        user.birth_day = form.cleaned_data.get("birth_day", user.birth_day)
        user.phone = form.cleaned_data.get("phone", user.phone)
        user.save()

        messages.success(self.request, "Ваш профиль успешно обновлён.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при обновлении профиля.")
        return super().form_invalid(form)


class PatientHistoryView(GreetingMixin, LoginRequiredMixin, ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "medsite/patient_history.html"
    paginate_by = 10

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user).order_by(
            "appointment_date"
        )


class DiagnosisUpdateView(
    GreetingMixin, LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Diagnosis
    form_class = DiagnosisForm
    template_name = "medsite/diagnosis_update.html"
    success_url = reverse_lazy("medsite:patient_history")

    def test_func(self):
        # Проверка прав доступа
        diagnosis = self.get_object()
        return self.request.user.is_staff or self.request.user == diagnosis.patient

    def get(self, request, appointment_id):
        try:
            appointment = get_object_or_404(Appointment, pk=appointment_id)
            diagnosis = get_object_or_404(Diagnosis, appointment=appointment)
            # Ваш код для отображения формы
            return render(
                request,
                "medsite/diagnosis_form.html",
                {"diagnosis": diagnosis, "appointment": appointment},
            )
        except Diagnosis.DoesNotExist:
            messages.error(request, "Диагноз не найден")
            return redirect("medsite/appointment_detail", pk=appointment_id)

    def post(self, request, appointment_id):
        try:
            appointment = get_object_or_404(Appointment, pk=appointment_id)
            diagnosis = get_object_or_404(Diagnosis, appointment=appointment)
            form = DiagnosisForm(request.POST, instance=diagnosis)
            if form.is_valid():
                form.save()
                return redirect("appointment_detail", pk=appointment_id)
            return render(request, "medsite/diagnosis_form.html", {"form": form})
        except Diagnosis.DoesNotExist:
            messages.error(request, "Диагноз не найден")
            return redirect("appointment_detail", pk=appointment_id)


class DiagnosisCreateView(GreetingMixin, View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = DiagnosisForm(user=request.user)
        return render(request, "medsite/diagnosis_form.html", {"form": form})

    def post(self, request):
        form = DiagnosisForm(request.POST, user=request.user)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.patient = request.user
            diagnosis.save()
            messages.success(request, "Диагноз успешно создан")
            return redirect("appointment_list")
        return render(request, "medsite/diagnosis_form.html", {"form": form})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
