from django.contrib import admin
from .models import ACARSMessage, SmartcarsProfile


@admin.register(ACARSMessage)
class ACARSMessageAdmin(admin.ModelAdmin):
    """
    Panel administracyjny dla wiadomości ACARS
    """
    list_display = [
        'timestamp', 'user', 'aircraft_id', 'flight_number', 
        'direction', 'latitude', 'longitude', 'altitude', 'speed'
    ]
    list_filter = [
        'direction', 'timestamp', 'aircraft_id', 'user'
    ]
    search_fields = [
        'aircraft_id', 'flight_number', 'user__username', 'user__email'
    ]
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('user', 'timestamp', 'direction')
        }),
        ('Lot', {
            'fields': ('aircraft_id', 'flight_number', 'route')
        }),
        ('Pozycja i parametry', {
            'fields': ('latitude', 'longitude', 'altitude', 'speed', 'heading')
        }),
        ('Czas', {
            'fields': ('time_off', 'time_on')
        }),
        ('Silnik', {
            'fields': ('engine_n1', 'engine_epr', 'fuel_flow')
        }),
        ('Inne', {
            'fields': ('pax_count', 'cost_index')
        }),
        ('ACARS', {
            'fields': ('transmission_mode', 'label', 'msg_number')
        }),
        ('Dane surowe', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optymalizuje zapytania do bazy danych
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(SmartcarsProfile)
class SmartcarsProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'api_key_preview', 'is_active', 'created_at', 'last_used')
    list_filter = ('is_active', 'created_at', 'last_used')
    search_fields = ('user__username', 'user__email', 'api_key')
    readonly_fields = ('created_at', 'last_used')
    
    def api_key_preview(self, obj):
        return f"{obj.api_key[:8]}..." if obj.api_key else "N/A"
    api_key_preview.short_description = "API Key"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user) 