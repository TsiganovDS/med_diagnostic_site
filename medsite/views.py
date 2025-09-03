from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
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
from medsite.forms import (
    AppointmentForm,
    DiagnosisForm,
    DoctorForm,
    DoctorRegistrationForm,
    FeedbackForm,
    PatientForm,
)
from users.models import CustomUser

from .models import Appointment, Diagnosis, Doctor, Patient, ServiceCategory


class GreetingMixin:
    def get_time_of_day_greeting(self):
        current_time = timezone.localtime()
        current_hour = current_time.hour
        if current_hour < 12:
            return "Доброе утро"
        elif 12 <= current_hour < 18:
            return "Добрый день"
        elif 18 <= current_hour < 24:
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


class ServicesListView(GreetingMixin, generic.ListView):
    model = ServiceCategory
    template_name = "medsite/services.html"
    context_object_name = "categories"

    def get_queryset(self):
        # Предварительно загружаем связанные услуги для оптимизации
        return ServiceCategory.objects.prefetch_related("services")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно добавить дополнительную информацию в контекст
        return context


class ContactsView(GreetingMixin, TemplateView):
    """Контроллер для отображения страницы контакты."""

    template_name = "medsite/contacts.html"


class SuccessView(GreetingMixin, TemplateView):
    template_name = "medsite/appointment_success.html"


class AppointmentCreateView(GreetingMixin, LoginRequiredMixin, CreateView):
    template_name = "medsite/appointment_form.html"
    form_class = AppointmentForm
    success_url = reverse_lazy("users:profile")
    model = Appointment

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["patient"] = self.request.user
        return initial

    def form_valid(self, form):
        try:
            # Проверяем, если поле patient не заполнено
            if not form.cleaned_data.get("patient"):
                form.instance.patient = self.request.user

            cleaned_data = form.cleaned_data

            # Создаем datetime объект
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
                return self.form_invalid(form)

            # Сохраняем запись
            appointment = form.save(commit=False)
            appointment.patient = self.request.user
            appointment.save()

            messages.success(self.request, "Запись успешно создана!")
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Произошла ошибка при сохранении: {str(e)}")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_model"] = get_user_model()
        return context


class AppointmentUpdateView(GreetingMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "medsite/appointments_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактирование записи"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def test_func(self):
        # Проверка прав доступа
        appointment = self.get_object()
        return self.request.user.is_staff or self.request.user == appointment.patient

    def get_success_url(self):
        # Можно настроить перенаправление
        return self.success_url

    def dispatch(self, request, *args, **kwargs):
        # Дополнительная проверка перед обработкой запроса
        self.object = self.get_object()
        if not self.test_func():
            return HttpResponseForbidden("У вас нет прав на редактирование этой записи")
        return super().dispatch(request, *args, **kwargs)


class AdminAppointmentCreateView(GreetingMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "medsite/admin_appointment_form.html"
    success_url = reverse_lazy("medsite:admin_appointment_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Запись"
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            appointment = form.save()

            service_name = (
                appointment.service.name if appointment.service else "Не указана"
            )
            service_description = (
                appointment.service.description if appointment.service else ""
            )

            send_mail(
                subject="📅 Запись на прием:",
                message=(
                    f"Здравствуйте, {appointment.patient.first_name}!\n\n"
                    f"Вы записаны на прием:\n"
                    f"Врач: {appointment.doctor.get_full_name()}\n"
                    f"Услуга: {service_name}\n"
                    f"Описание услуги: {service_description}\n"
                    f"Дата приема: {appointment.appointment_date}\n"
                    f"Время: {appointment.appointment_time}\n\n"
                    f"С уважением,\nКоманда Медицинской диагностики"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient.email],
                fail_silently=False,
            )

            messages.success(self.request, "Запись успешно обновлена")

            return response

        except Exception as e:
            # Если произошла ошибка при отправке письма
            messages.error(
                self.request, f"Произошла ошибка при обновлении записи: {str(e)}"
            )
            return self.form_invalid(form)


class AdminAppointmentsListView(GreetingMixin, UserPassesTestMixin, ListView):
    model = Appointment
    template_name = "medsite/admin_appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return (
            Appointment.objects.select_related("patient", "doctor__user")
            .prefetch_related("diagnoses")
            .order_by("-appointment_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_appointments"] = self.get_queryset().count()
        return context


class AppointmentListView(GreetingMixin, ListView):
    model = Appointment
    context_object_name = "appointments"
    template_name = "medsite/appointment_list.html"

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user).order_by(
            "appointment_date", "appointment_time"
        )


class AppointmentDetailView(GreetingMixin, DetailView):
    model = Appointment
    template_name = "medsite/appointment_detail.html"
    context_object_name = "appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.object

        # Безопасное получение связанных объектов
        try:
            context["diagnoses"] = (
                appointment.diagnoses.all() if appointment.diagnoses else []
            )
        except AttributeError:
            context["diagnoses"] = []

        # Другие связанные объекты
        try:
            context["another_related"] = (
                appointment.another_field.all() if appointment.another_field else []
            )
        except AttributeError:
            context["another_related"] = []

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
            settings, "ADMIN_EMAIL_LIST", ["dm.tsiganov@icloud.com"]
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


class DiagnosisUpdateView(GreetingMixin, UpdateView):
    model = Diagnosis
    form_class = DiagnosisForm
    template_name = "medsite/diagnosis_form.html"

    def get_object(self, queryset=None):
        # Получаем диагноз по diagnosis_id из URL
        return get_object_or_404(Diagnosis, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_success_url(self):
        # Используем правильный ключ для получения appointment_id
        return reverse(
            "medsite:appointment_detail", kwargs={"pk": self.kwargs["appointment_id"]}
        )


class DiagnosisCreateView(GreetingMixin, CreateView):
    model = Diagnosis
    form_class = DiagnosisForm
    template_name = "medsite/diagnosis_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        appointment_id = self.kwargs.get("appointment_id")
        if appointment_id:
            form.instance.appointment = get_object_or_404(
                Appointment, id=appointment_id
            )
            form.instance.patient = self.request.user  # Устанавливаем пользователя
            return super().form_valid(form)
        else:
            form.add_error(None, "Недостаточно данных для создания диагноза.")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse(
            "medsite:appointment_detail", kwargs={"pk": self.kwargs["appointment_id"]}
        )


class DiagnosisDetailView(GreetingMixin, DetailView):
    model = Diagnosis
    template_name = "medsite/diagnosis_detail.html"
    context_object_name = "diagnosis"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related("appointment").filter(
            appointment__patient=self.request.user
        )


class PatientListView(GreetingMixin, ListView):
    model = CustomUser
    template_name = "medsite/patients_list.html"
    context_object_name = "patients"
    paginate_by = 10

    def get_queryset(self):
        queryset = CustomUser.objects.filter(
            user_type="patient", doctor_profile__isnull=True
        ).order_by("last_name")

        # Добавляем поиск
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )

        return queryset


class PatientAppointmentsView(GreetingMixin, ListView):
    model = Appointment
    template_name = "medsite/patient_appointments.html"
    context_object_name = "appointments"

    def get_queryset(self):
        patient_id = self.kwargs["patient_id"]
        return Appointment.objects.filter(patient_id=patient_id).order_by(
            "-appointment_date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient_id"] = self.kwargs["patient_id"]
        return context
