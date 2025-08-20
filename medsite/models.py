from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django.template.defaultfilters import slugify
from django.utils import timezone

from users.models import CustomUser


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=[
        ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O+', 'O+'),
        ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('O-', 'O-')
    ], null=True, blank=True)


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    additional_info = models.TextField(blank=False, default='')

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


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
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
        verbose_name="Категория",
    )
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-псевдоним, генерируется автоматически из названия.",
    )
    short_description = models.TextField(
        verbose_name="Краткое описание (для списка)",
        help_text="Короткое описание услуги, до 200 символов.",
    )
    full_description = models.TextField(
        verbose_name="Полное описание (для детальной страницы)"
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Базовая цена",
        help_text="Оставьте пустым, если цена варьируется (см. пункты прайс-листа).",
    )

    duration_minutes = models.IntegerField(
        default=30,
        verbose_name="Примерная длительность услуги (минут)",
        help_text="Используется для расчета доступных слотов для записи.",
    )

    is_active = models.BooleanField(default=True, verbose_name="Активна")
    image = models.ImageField(
        upload_to="service_images/",
        blank=True,
        null=True,
        verbose_name="Изображение услуги",
    )

    doctors = models.ManyToManyField(
        "Doctor",
        blank=True,
        related_name="services",
        verbose_name="Врачи, предоставляющие услугу",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            count = 1
            while Service.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    """Модель записи к врачу"""
    patient = models.ForeignKey(CustomUser, related_name='appointments', null=False, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['appointment_date']

    @property
    def is_past_due(self):
        """Проверяет, прошла ли запись"""
        return self.appointment_date <= timezone.now() + timedelta(hours=1)

    def __str__(self):
        return f'Запись {self.patient.email} к {self.doctor}'
