from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['submitted_at']
