from django.db import models
from django.contrib.auth.models import User


class ACARSMessage(models.Model):
    # 1. Użytkownik
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Użytkownik, który odebrał lub wysłał wiadomość"
    )

    # 2. Identyfikacja lotu i trasa
    aircraft_id   = models.CharField(max_length=10, help_text="Rejestracja statku powietrznego")
    flight_number = models.CharField(max_length=10, blank=True, help_text="Numer lotu")
    route         = models.CharField(max_length=50, blank=True, help_text="Trasa: np. 'WAW-JFK'")

    # 3. Pozycja i ruch
    latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Szerokość geograficzna")
    longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Długość geograficzna")
    altitude   = models.IntegerField(null=True, blank=True, help_text="Wysokość w stopach")
    speed      = models.IntegerField(null=True, blank=True, help_text="Prędkość w węzłach (TAS/IAS)")
    heading    = models.IntegerField(null=True, blank=True, help_text="Kierunek w stopniach")

    # 4. Czasy OOOI i szacowane
    time_off         = models.TimeField(null=True, blank=True, help_text="OF – Time Off (odlot z bramki)")
    time_on          = models.TimeField(null=True, blank=True, help_text="ON – Time On (przylot na pas)")
    estimated_over   = models.TimeField(null=True, blank=True, help_text="EO – Estimated Time Over")
    estimated_ramp   = models.TimeField(null=True, blank=True, help_text="ERT – Estimated Ramp Time")

    # 5. Parametry silników i paliwa
    engine_n1        = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="N1 – prędkość turbiny niskiego stopnia")
    engine_epr       = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="EPR – Exhaust Pressure Ratio")
    fuel_flow        = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text="FF – Fuel Flow")
    fuel_on_board    = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="FOB – Fuel On Board")

    # 6. Stan systemów i utrzymanie
    maintenance_code = models.CharField(max_length=10, blank=True, help_text="MN – kod konserwacji")
    fault_report     = models.CharField(max_length=50, blank=True, help_text="FLR – opis błędu/usterki")

    # 7. Warunki pogodowe
    temperature_oat  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="OAT – Outside Air Temperature")
    wind_info        = models.CharField(max_length=50, blank=True, help_text="WND – informacje o wietrze")

    # 8. Pasażerowie i ładunek
    pax_count        = models.IntegerField(null=True, blank=True, help_text="PAX – liczba pasażerów")
    load_weight      = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="ZW – Zero Fuel Weight")

    # 9. Operacje i planowanie
    cost_index       = models.IntegerField(null=True, blank=True, help_text="CI – Cost Index")
    center_of_gravity= models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="CG – Center of Gravity")

    # 10. Komunikacja i nagłówki
    transmission_mode= models.CharField(max_length=4, blank=True, help_text="Tryb transmisji (A/B etc.)")
    label            = models.CharField(max_length=2, blank=True, help_text="Label – dwuznakowy kod wiadomości")
    msg_number       = models.IntegerField(null=True, blank=True, help_text="Msg No. – numer sekwencji wiadomości")

    # 11. Kierunek i znacznik czasu
    timestamp  = models.DateTimeField(auto_now_add=True, help_text="Data i czas odbioru lub wysłania")
    direction  = models.CharField(
        max_length=4,
        choices=[('IN', 'Incoming'), ('OUT', 'Outgoing')],
        help_text="Kierunek komunikatu"
    )

    # 12. Surowe dane
    payload    = models.JSONField(help_text="Pełny, surowy JSON komunikatu ACARS")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Komunikat ACARS"
        verbose_name_plural = "Komunikaty ACARS"

    def __str__(self):
        return f"{self.flight_number or self.aircraft_id} ({self.aircraft_id}) – {self.direction} @ {self.timestamp}"
