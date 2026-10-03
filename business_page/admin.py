from django.contrib import admin
from django.utils.html import format_html

from .models import CaseStudy, ContactSubmission, GeneratedAsset, Post, Subscriber


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'project_type', 'is_urgent', 'status', 'submitted_at']
    list_filter = ['status', 'project_type', 'is_urgent', 'submitted_at']
    search_fields = ['name', 'email', 'company', 'message']
    readonly_fields = ['submitted_at', 'source']
    list_editable = ['status']
    date_hierarchy = 'submitted_at'


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'confirmed_at', 'unsubscribed_at', 'created_at']
    list_filter = ['confirmed_at', 'unsubscribed_at']
    search_fields = ['email']
    readonly_fields = ['token', 'created_at']

    @admin.display(boolean=True)
    def is_active(self, obj):
        return obj.is_active


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ['client', 'title', 'status', 'featured', 'is_published', 'order']
    list_filter = ['status', 'featured', 'is_published']
    list_editable = ['featured', 'is_published', 'order']
    search_fields = ['client', 'title', 'summary']
    prepopulated_fields = {'slug': ('client',)}
    fieldsets = (
        (None, {'fields': ('slug', 'client', 'title', 'sector', 'summary', 'status', 'public_url')}),
        ('Classification', {'fields': ('layers', 'services', 'stack', 'scope_note')}),
        ('Narrative', {'fields': ('context', 'problem', 'system', 'implementation', 'outcome', 'outcomes')}),
        ('Architecture diagram', {'fields': ('architecture',), 'description':
            'JSON: {"nodes": [{"id","label","layer","x","y","detail"}], "edges": [["from","to"], ...]} — viewBox is 1000×560.'}),
        ('Media', {'fields': ('cover', 'cover_alt', 'cover_is_illustration', 'gallery')}),
        ('Display', {'fields': ('legacy_anchor', 'featured', 'order', 'is_published')}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'featured', 'is_published', 'published_at', 'reading_minutes']
    list_filter = ['topic', 'featured', 'is_published']
    list_editable = ['featured', 'is_published']
    search_fields = ['title', 'dek', 'body']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['reading_minutes', 'updated_at']
    fieldsets = (
        (None, {'fields': ('slug', 'title', 'dek', 'topic', 'author_name')}),
        ('Content', {'fields': ('body',), 'description': 'Markdown. Fenced code blocks are syntax-highlighted.'}),
        ('Display', {'fields': ('featured', 'is_published', 'published_at', 'reading_minutes', 'updated_at')}),
    )


@admin.register(GeneratedAsset)
class GeneratedAssetAdmin(admin.ModelAdmin):
    list_display = ['slot', 'model_slug', 'status', 'created_at', 'completed_at', 'preview']
    list_filter = ['status', 'model_slug']
    search_fields = ['slot', 'request_id', 'prompt']
    readonly_fields = ['request_id', 'created_at', 'updated_at', 'completed_at', 'result']

    @admin.display(description='Preview')
    def preview(self, obj):
        if not obj.result_url:
            return '—'
        return format_html('<a href="{}" target="_blank" rel="noopener">result ↗</a>', obj.result_url)
