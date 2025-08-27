from django.contrib import admin

from .models import Appointment, Feedback, Service, ServiceCategory


# Регистрация услуг
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name", "description")


# Регистрация категорий услуг
@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# Регистрация записей
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "service", "appointment_date", "status")
    list_filter = ("status", "appointment_date")
    search_fields = ("patient__email", "service__name")


# Регистрация модели обратной связи
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_answered")
    search_fields = ("name", "email", "subject", "message")
    list_filter = ("is_answered", "created_at")
    date_hierarchy = "created_at"


admin.site.register(Feedback, FeedbackAdmin)
