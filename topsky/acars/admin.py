from django.contrib import admin
from .models import SmartcarsProfile


@admin.register(SmartcarsProfile)
class SmartcarsProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'last_login', 'api_key_short')
    list_filter = ('created_at', 'last_login')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('api_key', 'acars_token', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('SmartCARS Credentials', {
            'fields': ('api_key', 'acars_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login')
        }),
    )
    
    def api_key_short(self, obj):
        """Show shortened API key for security"""
        if obj.api_key:
            return f"{obj.api_key[:8]}...{obj.api_key[-8:]}"
        return "No API key"
    api_key_short.short_description = "API Key"
    
    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of profiles
        return request.user.is_superuser 