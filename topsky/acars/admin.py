from django.contrib import admin
from .models import ACARSMessage


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
        return super().get_queryset(request).select_related('user') 