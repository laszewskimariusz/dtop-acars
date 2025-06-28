# smartCARS 3 API - Przewodnik integracji

## Opis

To jest 1:1 kompatybilne API smartCARS 3 dla Topsky Virtual Airlines, bazujące na oficjalnej specyfikacji phpVMS.

**URL API:** `https://yourdomain.com/api/smartcars/`

## Bazowane na oficjalnych specyfikacjach

- [smartCARS 3 phpVMS 5 API](https://github.com/invernyx/smartcars-3-phpvms5-api)
- [smartCARS 3 phpVMS 7 API](https://github.com/invernyx/smartcars-3-phpvms7-api)

## Endpointy API

### 1. Handler (Endpoint główny)
```
GET/POST /api/smartcars/
```

**Odpowiedź:**
```json
{
    "apiVersion": "1.0.2",
    "handler": {
        "name": "smartCARS 3 Django Handler",
        "version": "1.0.2",
        "author": "Topsky Virtual Airlines",
        "web": "https://dtopsky.topsky.app"
    },
    "phpvms": {
        "version": "7.0.0",
        "type": "Django Port"
    },
    "auth": true,
    "time": "2024-01-15T10:30:45Z"
}
```

### 2. Login (Logowanie)
```
POST /api/smartcars/login
Content-Type: application/x-www-form-urlencoded

username=pilot@example.com&password=your_password
```

**Odpowiedź:**
```json
{
    "pilotID": "LO0001",
    "session": "abc123def456...",
    "expiry": 1642243845,
    "firstName": "Jan",
    "lastName": "Kowalski",
    "email": "pilot@example.com"
}
```

### 3. User Info (Informacje o użytkowniku)
```
GET /api/smartcars/user?session=abc123def456...
```

**Odpowiedź:**
```json
{
    "pilot_id": 1,
    "name": "Jan Kowalski",
    "email": "pilot@example.com",
    "country": "PL",
    "timezone": "Europe/Warsaw",
    "opt_in": true,
    "status": 1,
    "total_flights": 15,
    "total_hours": 0,
    "curr_airport_id": "EPWA"
}
```

### 4. Schedules (Rozkłady lotów)
```
GET /api/smartcars/schedules?session=abc123def456...
```

### 5. Aircraft (Samoloty)
```
GET /api/smartcars/aircraft?session=abc123def456...
```

### 6. Airports (Lotniska)
```
GET /api/smartcars/airports?session=abc123def456...
```

### 7. Position Reporting (Raportowanie pozycji)
```
POST /api/smartcars/position
Content-Type: application/x-www-form-urlencoded

session=abc123def456...&lat=52.1657&lng=20.9671&altitude=5000&heading=270&speed=250&aircraft=SP-TSA
```

### 8. PIREP Submission (Zgłaszanie raportu lotu)
```
POST /api/smartcars/pirep
Content-Type: application/x-www-form-urlencoded

session=abc123def456...&flight_number=TS001&aircraft_id=1&departure=EPWA&arrival=EGLL&flight_time=120&distance=1200
```

## Uwierzytelnianie

API obsługuje dwa tryby uwierzytelniania:

1. **Hasło Django** - standardowe hasło użytkownika z systemu
2. **SmartCARS API Key** - dedykowany klucz API dla każdego użytkownika

### Dla logowania (endpoint /login):
- Używa hasła Django użytkownika
- Zwraca SmartCARS API Key jako "session"

### Dla pozostałych endpointów:
- Używa SmartCARS API Key otrzymanego przy logowaniu
- Przekazuje jako parametr `session` lub `api_key`

## Kompatybilność

To API jest w 100% kompatybilne z:
- TFDi Design smartCARS 3
- phpVMS 5/7 standardowym API
- Oficjalną specyfikacją REST API smartCARS

## Konfiguracja w smartCARS Central

1. Wejdź do smartCARS Central
2. Ustaw **Script URL** na: `https://yourdomain.com/api/smartcars/`
3. Wybierz odpowiedni **Plugin** (standardowy phpVMS 7)
4. Zapisz konfigurację

## Debugowanie

Do debugowania logowania dostępny jest specjalny endpoint:
```
GET /acars/api/debug/
```

Pokazuje ostatnie 20 requestów z danymi debugowania.

## Problemy z logowaniem

Jeśli smartCARS nie może się zalogować:

1. **Sprawdź dane logowania:**
   - Użyj **emaila** jako username
   - Użyj **hasła Django** (nie token!)

2. **Sprawdź URL-e:**
   - API: `https://yourdomain.com/api/smartcars/`
   - Login: `https://yourdomain.com/api/smartcars/login`

3. **Sprawdź logi:**
   - `tail -f logs/django.log` (debugging info)
   - `GET /acars/api/debug/` (ostatnie requesty)

4. **Upewnij się że:**
   - Użytkownik ma aktywne konto
   - Ma utworzony SmartcarsProfile
   - Serwer akceptuje `Content-Type: application/x-www-form-urlencoded`

## Różnice względem poprzedniej wersji

### ✅ Nowa wersja (phpVMS API):
- Prostsze, standardowe endpointy
- 1:1 kompatybilność z oficjalnym API
- Jeden czysty plik API (`phpvms_api.py`)
- Logowanie hasłem Django + zwracany API key

### ❌ Stara wersja (usunięta):
- Skomplikowane wielopoziomowe API
- Wielu nakładających się endpointów
- JWT + API keys + Basic Auth
- Problemy z kompatybilnością

## Pomoc techniczna

W przypadku problemów:
1. Sprawdź logi Django
2. Użyj `/acars/api/debug/` do debugowania
3. Porównaj z działającymi wirtualnymi liniami (np. Walker Air Transport)
4. Skontaktuj się z administratorem systemu 