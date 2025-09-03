import calendar
from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_day = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-псевдоним, генерируется автоматически из названия.",
    )
    description = models.TextField(blank=True, verbose_name="Описание категории")
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения",
        help_text="Чем меньше число, тем выше категория в списке.",
    )

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            count = 1
            while ServiceCategory.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="services"
    )
    name = models.CharField("Название услуги", max_length=100)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    TYPES = [
        ("узи", "УЗИ-аппарат"),
        ("рентген", "Рентген-аппарат"),
        ("экг", "ЭКГ-аппарат"),
        ("мрт", "МРТ"),
        ("кт", "КТ"),
        ("", "Без оборудования"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    equipment_type = models.CharField(
        max_length=50, choices=TYPES, blank=True, default=""
    )

    specialization = models.TextField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField(default=time(9, 0))
    end_time = models.TimeField(default=time(10, 0))

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class Schedule(models.Model):
    """Расписание врача"""

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="schedule"
    )
    weekday = models.IntegerField(  # 0-понедельник, 6-воскресенье
        choices=[(i, calendar.day_name[i]) for i in range(7)]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("doctor", "weekday", "start_time", "end_time")


class Appointment(models.Model):
    """Модель записи к врачу"""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )

    reason = models.TextField(
        max_length=100, blank=True, null=True, verbose_name="Причина обращения"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    is_confirmed = models.BooleanField(default=False)
    diagnoses = models.ForeignKey(
        "Diagnosis",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    description = models.TextField(blank=True, verbose_name="Диагноз")
    results = models.FileField(
        upload_to="diagnostics/", blank=True, null=True, verbose_name="Результаты"
    )
    notes = models.TextField(blank=True, verbose_name="Примечания врача")

    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, related_name="appointments"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидает подтверждения"),
            ("confirmed", "Подтверждена"),
            ("cancelled", "Отменена"),
            ("completed", "Завершена"),
        ],
        default="pending",
    )

    def is_working_time(self):
        appointment_datetime = datetime.combine(
            self.appointment_date, self.appointment_time
        )

        doctor_start_datetime = datetime.combine(
            self.appointment_date, self.doctor.start_time
        )

        doctor_end_datetime = datetime.combine(
            self.appointment_date, self.doctor.end_time
        )

        return doctor_start_datetime <= appointment_datetime <= doctor_end_datetime

    def clean(self):
        if not self.appointment_date or not self.appointment_time:
            raise ValidationError("Дата и время должны быть заполнены")

        # Создаем полную дату и время
        full_datetime = datetime.combine(self.appointment_date, self.appointment_time)

        if timezone.is_aware(timezone.now()):
            full_datetime = timezone.make_aware(full_datetime)

        # Проверяем, что дата не в прошлом
        if full_datetime < timezone.now():
            raise ValidationError("Дата записи не может быть в прошлом")

        if self.service:
            try:
                end_time = full_datetime + timedelta(
                    minutes=self.service.duration_minutes
                )

                overlapping_appointments = Appointment.objects.filter(
                    doctor=self.doctor,
                    appointment_date=self.appointment_date,
                    appointment_time__range=(full_datetime.time(), end_time.time()),
                )

                if self.pk:
                    overlapping_appointments = overlapping_appointments.exclude(
                        pk=self.pk
                    )

                if overlapping_appointments.exists():
                    raise ValidationError("У врача уже есть запись на это время")

            except AttributeError:
                raise ValidationError("Некорректная длительность услуги")

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("medsite:appointment_detail", kwargs={"pk": self.pk})

    def get_results_link(self):
        if self.results:
            return f'<a href="{self.results.url}" download>Скачать результаты</a>'
        return "Нет результатов"

    get_results_link.allow_tags = True

    def __str__(self):
        patient_name = self.patient.get_full_name() if self.patient else "Неизвестно"
        doctor_name = self.doctor.get_full_name() if self.doctor else "Неизвестно"

        date_str = ""
        if self.appointment_date and self.appointment_time:
            date_str = datetime.combine(
                self.appointment_date, self.appointment_time
            ).strftime("%d.%m.%Y %H:%M")

        return f"Запись {patient_name} к {doctor_name} на {date_str}"


class Diagnosis(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пациент"
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="diagnoses_set",
        null=True,
        blank=True,
    )
    diagnosis_date = models.DateField()
    description = models.TextField(verbose_name="Описание диагноза")

    def __str__(self):
        return f"Диагноз для {self.patient}: {self.text[:50]}..."


class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField("Имя", max_length=100)
    email = models.EmailField("Email")
    subject = models.CharField("Тема", max_length=200)
    message = models.TextField("Сообщение")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    is_answered = models.BooleanField("Ответ получен", default=False)

    def __str__(self):
        return f"{self.subject} от {self.name}"
