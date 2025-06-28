from django.db import models
from django.contrib.auth.models import User


class ACARSMessage(models.Model):
    """
    Model dla wiadomości ACARS (Aircraft Communications Addressing and Reporting System)
    Przechowuje wszystkie dane pobierane z urządzeń/systemów ACARS
    """
    # Relacja do użytkownika
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    
    # Podstawowe informacje o locie
    aircraft_id = models.CharField(max_length=10, verbose_name="ID Samolotu")
    flight_number = models.CharField(max_length=10, blank=True, verbose_name="Numer Lotu")
    route = models.CharField(max_length=50, blank=True, verbose_name="Trasa")
    
    # Pozycja i parametry lotu
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Szerokość geograficzna")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Długość geograficzna")
    altitude = models.IntegerField(null=True, blank=True, verbose_name="Wysokość (ft)")
    speed = models.IntegerField(null=True, blank=True, verbose_name="Prędkość (kts)")
    heading = models.IntegerField(null=True, blank=True, verbose_name="Kurs (°)")
    
    # Czasy OOOI (Out-Off-On-In)
    time_off = models.TimeField(null=True, blank=True, verbose_name="Czas startu")
    time_on = models.TimeField(null=True, blank=True, verbose_name="Czas lądowania")
    
    # Parametry silnika
    engine_n1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="N1 (%)")
    engine_epr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="EPR")
    fuel_flow = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Przepływ paliwa (kg/h)")
    
    # Inne parametry lotu
    pax_count = models.IntegerField(null=True, blank=True, verbose_name="Liczba pasażerów")
    cost_index = models.IntegerField(null=True, blank=True, verbose_name="Indeks kosztów")
    
    # Parametry wiadomości ACARS
    transmission_mode = models.CharField(max_length=4, blank=True, verbose_name="Tryb transmisji")
    label = models.CharField(max_length=2, blank=True, verbose_name="Etykieta wiadomości")
    msg_number = models.IntegerField(null=True, blank=True, verbose_name="Numer wiadomości")
    
    # Metadane
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Czas otrzymania")
    direction = models.CharField(
        max_length=4, 
        choices=[
            ('IN', 'Przychodzące'),
            ('OUT', 'Wychodzące')
        ],
        verbose_name="Kierunek wiadomości"
    )
    
    # Pełne dane JSON z urządzenia ACARS
    payload = models.JSONField(verbose_name="Pełne dane JSON")
    
    class Meta:
        verbose_name = "Wiadomość ACARS"
        verbose_name_plural = "Wiadomości ACARS"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['aircraft_id', '-timestamp']),
            models.Index(fields=['flight_number', '-timestamp']),
        ]
    
    def __str__(self):
        return f"ACARS {self.aircraft_id} - {self.flight_number or 'N/A'} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})" 