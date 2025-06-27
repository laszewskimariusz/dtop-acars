# System ACARS - Smartcars 3

System ACARS (Aircraft Communications Addressing and Reporting System) dla Smartcars 3 umożliwia komunikację z samolotami i zarządzanie komunikatami lotniczymi.

## Funkcjonalności

### Backend (Django + DRF)
- **Model ACARSMessage** - kompletny model z wszystkimi polami ACARS
- **API REST** - endpoints do zarządzania komunikatami
- **Uwierzytelnianie JWT** - bezpieczne logowanie
- **Panel administratora** - zarządzanie komunikatami
- **Automatyczne timestampy** - śledzenie czasu komunikatów

### Frontend (HTML + JavaScript)
- **Dashboard ACARS** - interfejs webowy
- **Logowanie JWT** - bezpieczna autentykacja
- **Wysyłanie komunikatów** - formularz z walidacją
- **Wyświetlanie komunikatów** - tabela z filtrowaniem
- **Szablony** - gotowe wzorce komunikatów
- **Auto-refresh** - automatyczne odświeżanie co 30s

## Pola modelu ACARSMessage

### Podstawowe
- `user` - użytkownik (ForeignKey)
- `timestamp` - czas komunikatu (auto)
- `direction` - kierunek (IN/OUT)

### Identyfikacja lotu
- `aircraft_id` - rejestracja samolotu
- `flight_number` - numer lotu  
- `route` - trasa (np. WAW-JFK)

### Pozycja i ruch
- `latitude` - szerokość geograficzna
- `longitude` - długość geograficzna
- `altitude` - wysokość (stopy)
- `speed` - prędkość (węzły)
- `heading` - kierunek (stopnie)

### Czasy OOOI
- `time_off` - Time Off (odlot z bramki)
- `time_on` - Time On (przylot na pas)
- `estimated_over` - Estimated Time Over
- `estimated_ramp` - Estimated Ramp Time

### Parametry silników i paliwa
- `engine_n1` - N1 (prędkość turbiny)
- `engine_epr` - EPR (Exhaust Pressure Ratio)
- `fuel_flow` - przepływ paliwa
- `fuel_on_board` - paliwo na pokładzie

### Stan systemów
- `maintenance_code` - kod konserwacji
- `fault_report` - raport błędów

### Warunki pogodowe
- `temperature_oat` - temperatura zewnętrzna
- `wind_info` - informacje o wietrze

### Pasażerowie i ładunek
- `pax_count` - liczba pasażerów
- `load_weight` - masa bez paliwa

### Operacje
- `cost_index` - indeks kosztów
- `center_of_gravity` - środek ciężkości

### Komunikacja
- `transmission_mode` - tryb transmisji
- `label` - kod wiadomości
- `msg_number` - numer sekwencji

### Surowe dane
- `payload` - pełny JSON komunikatu

## API Endpoints

### Uwierzytelnianie
```
POST /api/token/ - uzyskaj token JWT
POST /api/token/refresh/ - odśwież token
```

### Komunikaty ACARS
```
GET /acars/api/messages/ - lista komunikatów użytkownika
POST /acars/api/messages/ - wyślij nowy komunikat
GET /acars/api/messages/{id}/ - szczegóły komunikatu
PUT /acars/api/messages/{id}/ - aktualizuj komunikat
DELETE /acars/api/messages/{id}/ - usuń komunikat
```

### Dashboard
```
GET /acars/ - interfejs webowy ACARS
```

## Przykłady użycia

### Logowanie (JavaScript)
```javascript
const response = await fetch('/api/token/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: 'pilot', password: 'haslo123'})
});
const {access, refresh} = await response.json();
```

### Wysyłanie komunikatu
```javascript
const messageData = {
    aircraft_id: 'SP-LOT',
    flight_number: 'LO123',
    direction: 'OUT',
    latitude: 52.165726,
    longitude: 20.967130,
    altitude: 35000,
    payload: {
        type: 'position_report',
        fuel_remaining: 12500,
        speed: 480
    }
};

await fetch('/acars/api/messages/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + accessToken
    },
    body: JSON.stringify(messageData)
});
```

### Pobieranie komunikatów
```javascript
const response = await fetch('/acars/api/messages/', {
    headers: {'Authorization': 'Bearer ' + accessToken}
});
const messages = await response.json();
```

## Szablony komunikatów

System zawiera gotowe szablony:

### Raport pozycji
```json
{
    "type": "position_report",
    "fuel_remaining": 12500,
    "speed": 480,
    "heading": 270
}
```

### Odlot
```json
{
    "type": "departure",
    "gate": "A12",
    "fuel_on_board": 18500,
    "passengers": 180
}
```

### Przylot
```json
{
    "type": "arrival",
    "gate": "B7",
    "fuel_remaining": 4200,
    "flight_time": "02:15"
}
```

### Raport paliwa
```json
{
    "type": "fuel_report",
    "fuel_flow": 2400,
    "fuel_remaining": 8900,
    "endurance": "03:42"
}
```

## Instalacja i konfiguracja

1. Dodaj `'acars'` do `INSTALLED_APPS` w settings.py
2. Wykonaj migracje: `python manage.py migrate`
3. Stwórz superusera: `python manage.py createsuperuser`
4. Uruchom serwer: `python manage.py runserver`
5. Otwórz http://127.0.0.1:8000/acars/

## Bezpieczeństwo

- Wszystkie endpointy API wymagają uwierzytelniania
- Użytkownicy widzą tylko swoje komunikaty
- Tokeny JWT z rotacją refresh tokenów
- Walidacja danych na poziomie serializerów

## Panel administratora

Dostępny w `/admin/` - umożliwia:
- Przeglądanie wszystkich komunikatów
- Filtrowanie po kierunku, czasie, samolocie
- Edycję szczegółów komunikatów
- Wyszukiwanie po numerze lotu i rejestracji 