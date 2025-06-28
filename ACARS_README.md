# 🛩️ System ACARS - Django API

Kompletny system ACARS (Aircraft Communications Addressing and Reporting System) zintegrowany z Django, wykorzystujący JWT authentication i tę samą bazę użytkowników co strona WWW.

## 📋 Spis treści
- [Funkcjonalności](#funkcjonalności)
- [Konfiguracja](#konfiguracja)
- [Endpointy API](#endpointy-api)
- [Model danych](#model-danych)
- [Przykład użycia](#przykład-użycia)
- [Klient ACARS](#klient-acars)

## ✨ Funkcjonalności

- **JWT Authentication** - Bezpieczne uwierzytelnianie z tokenami dostępu (12h) i odświeżania (7 dni)
- **Pełny model ACARS** - Wszystkie standardowe pola wiadomości ACARS
- **REST API** - Kompletne CRUD operacje dla wiadomości ACARS
- **Integracja z użytkownikami** - Używa tej samej bazy użytkowników co strona WWW
- **Bulk operations** - Możliwość wysyłania wielu wiadomości jednocześnie
- **Admin panel** - Pełny panel administracyjny Django
- **Automatyczne indeksowanie** - Optymalizacja wydajności bazy danych

## ⚙️ Konfiguracja

### 1. Wymagania
System został skonfigurowany w `settings.py` z następującymi ustawieniami:

```python
# Aplikacje
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'acars',
]

# DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### 2. Migracje
```bash
python manage.py makemigrations acars
python manage.py migrate
```

## 🌐 Endpointy API

### smartCARS Compatibility (Legacy)
- `GET /acars/api/` - Główny handler smartCARS (info o API)
- `POST /acars/api/login/` - Logowanie smartCARS (zwraca JWT jako api_key)
- `GET /acars/api/user/` - Informacje o użytkowniku (wymaga api_key)
- `GET /acars/api/airports/` - Lista lotnisk
- `GET /acars/api/aircraft/` - Lista samolotów
- `GET /acars/api/schedules/` - Lista rozkładów

### Nowoczesne JWT Authentication
- `POST /api/auth/login/` - Logowanie i pobranie tokenów JWT
- `POST /api/auth/refresh/` - Odświeżenie tokena dostępu
- `GET /acars/api/ping/` - Test połączenia

### Wiadomości ACARS (REST API)
- `GET /acars/api/messages/` - Lista wiadomości użytkownika
- `POST /acars/api/messages/` - Nowa wiadomość ACARS
- `GET /acars/api/messages/{id}/` - Szczegóły wiadomości
- `PUT /acars/api/messages/{id}/` - Aktualizacja wiadomości
- `DELETE /acars/api/messages/{id}/` - Usunięcie wiadomości

### Dodatkowe endpointy
- `GET /acars/api/messages/latest/` - Najnowsza wiadomość
- `GET /acars/api/messages/stats/` - Statystyki użytkownika
- `POST /acars/api/bulk-create/` - Masowe tworzenie wiadomości

## 📊 Model danych

Model `ACARSMessage` zawiera wszystkie standardowe pola ACARS:

```python
class ACARSMessage(models.Model):
    # Relacja do użytkownika
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Podstawowe informacje o locie
    aircraft_id = models.CharField(max_length=10)
    flight_number = models.CharField(max_length=10, blank=True)
    route = models.CharField(max_length=50, blank=True)
    
    # Pozycja i parametry lotu
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    altitude = models.IntegerField(null=True, blank=True)  # ft
    speed = models.IntegerField(null=True, blank=True)     # kts
    heading = models.IntegerField(null=True, blank=True)   # degrees
    
    # Czasy OOOI (Out-Off-On-In)
    time_off = models.TimeField(null=True, blank=True)
    time_on = models.TimeField(null=True, blank=True)
    
    # Parametry silnika
    engine_n1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    engine_epr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fuel_flow = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    
    # Inne parametry
    pax_count = models.IntegerField(null=True, blank=True)
    cost_index = models.IntegerField(null=True, blank=True)
    
    # Parametry wiadomości ACARS
    transmission_mode = models.CharField(max_length=4, blank=True)
    label = models.CharField(max_length=2, blank=True)
    msg_number = models.IntegerField(null=True, blank=True)
    
    # Metadane
    timestamp = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=4, choices=[('IN','Incoming'),('OUT','Outgoing')])
    payload = models.JSONField()  # Pełne dane JSON
```

## 🚀 Przykład użycia

### 1. Logowanie
```python
import requests

# Logowanie
response = requests.post("https://twoja-domena.com/api/auth/login/", json={
    "username": "pilot123",
    "password": "haslo123"
})

tokens = response.json()
access_token = tokens['access']
```

### 2. Wysyłanie wiadomości ACARS
```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

acars_data = {
    "aircraft_id": "SP-ABC",
    "flight_number": "TS001",
    "route": "EPWA-EGLL",
    "latitude": 52.1657,
    "longitude": 20.9671,
    "altitude": 35000,
    "speed": 480,
    "heading": 270,
    "direction": "OUT",
    "payload": {
        "timestamp": "2024-01-15T14:30:00Z",
        "simulator": "X-Plane 12",
        "aircraft_type": "Boeing 737-800"
    }
}

response = requests.post(
    "https://twoja-domena.com/acars/api/messages/",
    json=acars_data,
    headers=headers
)
```

### 3. Pobieranie statystyk
```python
response = requests.get(
    "https://twoja-domena.com/acars/api/messages/stats/",
    headers=headers
)

stats = response.json()
print(f"Łączna liczba wiadomości: {stats['total_messages']}")
print(f"Unikalne samoloty: {stats['unique_aircraft']}")
```

## 🖥️ Klient ACARS

W pliku `acars_client_example.py` znajduje się kompletny przykład klienta ACARS z następującymi funkcjonalnościami:

### Główne funkcje:
- **Automatyczne logowanie** z retry przy błędach
- **Automatyczne odświeżanie tokenów** przy wygaśnięciu
- **Wysyłanie pojedynczych wiadomości**
- **Wysyłanie wiadomości zbiorczych**
- **Symulacja pełnego lotu** z danymi w czasie rzeczywistym
- **Obsługa błędów** i retry logic

### Użycie klienta:
1. Edytuj zmienne `USERNAME`, `PASSWORD`, `API_BASE_URL`
2. Uruchom: `python acars_client_example.py`
3. Wybierz opcję z menu

### Przykład symulacji lotu:
```bash
python acars_client_example.py
# Wybierz opcję "3. Symuluj lot"
```

Klient automatycznie:
- Zaloguje się do API
- Wyśle dane startu (time_off)
- Będzie wysyłać pozycję co 30 sekund
- Wyśle dane lądowania (time_on)

## 🔧 Panel administracyjny

System jest w pełni zintegrowany z panelem administracyjnym Django:

1. Wejdź na `/admin/`
2. Sekcja **ACARS System** → **Wiadomości ACARS**
3. Dostępne funkcje:
   - Przeglądanie wszystkich wiadomości
   - Filtrowanie po użytkowniku, samolotach, czasie
   - Wyszukiwanie po numerach lotów
   - Szczegółowy widok z wszystkimi danymi

## 📈 Monitoring i statystyki

### Endpoint statystyk:
`GET /acars/api/messages/stats/`

Zwraca:
```json
{
    "total_messages": 1250,
    "incoming_messages": 625,
    "outgoing_messages": 625,
    "unique_aircraft": 12,
    "unique_flights": 89
}
```

### Najnowsza wiadomość:
`GET /acars/api/messages/latest/`

## 🛠️ Rozwiązywanie problemów

### Problem z tokenem 401:
- Sprawdź czy token nie wygasł
- Użyj endpointu `/api/auth/refresh/`
- Przykład automatycznego odświeżania w `acars_client_example.py`

### Problem z danymi:
- Sprawdź format JSON w polu `payload`
- Wszystkie pola oprócz `user` i `timestamp` są opcjonalne
- Pole `direction` musi być 'IN' lub 'OUT'

### Problem z bazą danych:
```bash
python manage.py makemigrations acars
python manage.py migrate
```

## 📚 Integracja z smartCARS

System jest w pełni kompatybilny z smartCARS 3 przez legacy endpoints:

### ✅ Web Script URL dla smartCARS 3:
```
https://dtopsky.topsky.app/acars/api/
```

Ten URL zwraca odpowiedź w formacie smartCARS[^1]:
```json
{
  "apiVersion": "1.0.0",
  "handler": {
    "name": "Django ACARS Handler",
    "version": "1.0.0",
    "author": "Topsky Virtual Airlines",
    "website": "https://dtopsky.topsky.app"
  },
  "status": "success",
  "response": "smartCARS API Handler is active and ready",
  "data": {
    "platform": "Django",
    "features": ["ACARS", "Position Reporting", "Flight Tracking", "Authentication"],
    "endpoints": {
      "login": "/acars/api/login",
      "user": "/acars/api/user",
      "schedules": "/acars/api/schedules",
      "aircraft": "/acars/api/aircraft",
      "airports": "/acars/api/airports"
    }
  }
}
```

### 🔧 Konfiguracja smartCARS 3:
1. **Web Script URL:** `https://dtopsky.topsky.app/acars/api/`
2. **Username/Password:** Te same co do strony WWW
3. Po zalogowaniu otrzymasz JWT token jako `api_key`
4. System automatycznie mapuje dane smartCARS na nowy model Django

### 💡 Mapowanie danych smartCARS:
```python
# smartCARS → Django ACARS
smartcars_data = get_smartcars_data()
acars_message = {
    "aircraft_id": smartcars_data.get("aircraft_icao"),
    "flight_number": smartcars_data.get("flight_number"),
    "latitude": smartcars_data.get("position", {}).get("lat"),
    "longitude": smartcars_data.get("position", {}).get("lng"),
    "altitude": smartcars_data.get("altitude"),
    "speed": smartcars_data.get("groundspeed"),
    "heading": smartcars_data.get("heading"),
    "direction": "OUT",
    "payload": smartcars_data  # Pełne dane smartCARS w JSON
}
```

---

## 🎯 Podsumowanie

System ACARS jest teraz w pełni skonfigurowany i gotowy do użycia. Główne korzyści:

✅ **Bezpieczny** - JWT authentication z blacklistą tokenów  
✅ **Kompletny** - Wszystkie standardowe pola ACARS  
✅ **Kompatybilny** - Obsługuje istniejący URL `https://dtopsky.topsky.app/acars/api/`[^1]  
✅ **Skalowalny** - Optymalizacja bazy danych z indeksami  
✅ **Elastyczny** - API REST z pełnym CRUD  
✅ **Zintegrowany** - Ta sama baza użytkowników co strona WWW  
✅ **smartCARS Ready** - Pełna kompatybilność z smartCARS 3  
✅ **Dokumentowany** - Pełne przykłady kodu i dokumentacja  

### 🚀 Gotowe do użycia z:
- **smartCARS 3** - Użyj URL: `https://dtopsky.topsky.app/acars/api/`
- **FSUIPC/SimConnect** - Użyj przykładowego klienta Python 
- **Dowolny system ACARS** - REST API z JWT authentication

[^1]: Zgodnie z wynikami testów, endpoint już działa i zwraca prawidłową odpowiedź smartCARS. 