import calendar

from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone, duration

from users.models import CustomUser


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ("A+", "A+"),
            ("B+", "B+"),
            ("AB+", "AB+"),
            ("O+", "O+"),
            ("A-", "A-"),
            ("B-", "B-"),
            ("AB-", "AB-"),
            ("O-", "O-"),
        ],
        null=True,
        blank=True,
    )

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
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField('Название услуги', max_length=100)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    TYPES = [
        ('узи', 'УЗИ-аппарат'),
        ('рентген', 'Рентген-аппарат'),
        ('экг', 'ЭКГ-аппарат'),
        ('мрт', 'МРТ'),
        ('кт', 'КТ'),
        ('', 'Без оборудования')
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    equipment_type = models.CharField(
        max_length=50,
        choices=TYPES,
        blank=True,
        default=''
    )

    specialization = models.TextField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def is_working_time(self, appointment_datetime):
        # Получаем расписание врача
        schedule = self.schedule.filter(
            weekday=appointment_datetime.weekday(),
            is_active=True
        ).first()

        if not schedule:
            return False

        appointment_time = appointment_datetime.time()
        return schedule.start_time <= appointment_time <= schedule.end_time

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class Schedule(models.Model):
    """Расписание врача"""
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    weekday = models.IntegerField(  # 0-понедельник, 6-воскресенье
        choices=[(i, calendar.day_name[i]) for i in range(7)]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor', 'weekday', 'start_time', 'end_time')


class Appointment(models.Model):
    """Модель записи к врачу"""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments')

    appointment_date = models.DateTimeField()
    appointment_time = models.TimeField()
    reason = models.TextField(max_length=100, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает подтверждения'),
            ('confirmed', 'Подтверждена'),
            ('cancelled', 'Отменена'),
            ('completed', 'Завершена')
        ],
        default='pending'
    )

    def get_full_datetime(self):
        # Проверяем, что дата и время существуют
        if self.appointment_date and self.appointment_time:
            return datetime.combine(self.appointment_date, self.appointment_time)
        return None

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
                end_time = full_datetime + timedelta(minutes=self.service.duration_minutes)

                # Добавляем проверку на пересечение записей
                overlapping_appointments = Appointment.objects.filter(
                    doctor=self.doctor,
                    appointment_date=self.appointment_date,
                    appointment_time__range=(
                        full_datetime.time(),
                        end_time.time()
                    )
                )

                if self.pk:
                    overlapping_appointments = overlapping_appointments.exclude(pk=self.pk)

                if overlapping_appointments.exists():
                    raise ValidationError("У врача уже есть запись на это время")

            except AttributeError:
                raise ValidationError("Некорректная длительность услуги")


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    subject = models.CharField('Тема', max_length=200)
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_answered = models.BooleanField('Ответ получен', default=False)

    def __str__(self):
        return f"{self.subject} от {self.name}"



