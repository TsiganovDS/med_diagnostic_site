from django.contrib import admin
from .models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_answered')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('is_answered', 'created_at')
    date_hierarchy = 'created_at'

admin.site.register(Feedback, FeedbackAdmin)

