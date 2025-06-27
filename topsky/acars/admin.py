from django.contrib import admin
from .models import ACARSMessage


@admin.register(ACARSMessage)
class ACARSMessageAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'flight_number', 'aircraft_id', 'direction', 'route', 'user']
    list_filter = ['direction', 'timestamp', 'aircraft_id']
    search_fields = ['flight_number', 'aircraft_id', 'route']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('user', 'direction', 'timestamp')
        }),
        ('Identyfikacja lotu', {
            'fields': ('aircraft_id', 'flight_number', 'route')
        }),
        ('Pozycja i ruch', {
            'fields': ('latitude', 'longitude', 'altitude', 'speed', 'heading'),
            'classes': ('collapse',)
        }),
        ('Czasy OOOI', {
            'fields': ('time_off', 'time_on', 'estimated_over', 'estimated_ramp'),
            'classes': ('collapse',)
        }),
        ('Parametry silników i paliwa', {
            'fields': ('engine_n1', 'engine_epr', 'fuel_flow', 'fuel_on_board'),
            'classes': ('collapse',)
        }),
        ('Stan systemów', {
            'fields': ('maintenance_code', 'fault_report'),
            'classes': ('collapse',)
        }),
        ('Warunki pogodowe', {
            'fields': ('temperature_oat', 'wind_info'),
            'classes': ('collapse',)
        }),
        ('Pasażerowie i ładunek', {
            'fields': ('pax_count', 'load_weight'),
            'classes': ('collapse',)
        }),
        ('Operacje', {
            'fields': ('cost_index', 'center_of_gravity'),
            'classes': ('collapse',)
        }),
        ('Komunikacja', {
            'fields': ('transmission_mode', 'label', 'msg_number'),
            'classes': ('collapse',)
        }),
        ('Surowe dane', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
    )
