#!/usr/bin/env python3
"""
Przykładowy klient ACARS dla Django API
Pokazuje jak się logować za pomocą JWT i wysyłać dane ACARS
"""

import requests
import json
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Konfiguracja
API_BASE_URL = "https://dtopsky.topsky.app"  # Zmień na swój URL
USERNAME = "twoja_nazwa_uzytkownika"  # Zmień na swoje dane
PASSWORD = "twoje_haslo"  # Zmień na swoje dane

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ACARSClient:
    """
    Klient ACARS do komunikacji z Django API
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.session = requests.Session()
    
    def login(self) -> bool:
        """
        Loguje się do API i pobiera tokeny JWT
        """
        login_url = f"{self.base_url}/api/auth/login/"
        
        try:
            response = self.session.post(
                login_url,
                json={
                    "username": self.username,
                    "password": self.password
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access')
                self.refresh_token = tokens.get('refresh')
                
                # Ustawia header Authorization dla przyszłych żądań
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("✅ Logowanie pomyślne")
                logger.info(f"Access token: {self.access_token[:50]}...")
                logger.info(f"Refresh token: {self.refresh_token[:50]}...")
                return True
            else:
                logger.error(f"❌ Błąd logowania: {response.status_code}")
                logger.error(f"Odpowiedź: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Wyjątek podczas logowania: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Odświeża token dostępu
        """
        if not self.refresh_token:
            logger.error("❌ Brak refresh token")
            return False
        
        refresh_url = f"{self.base_url}/api/auth/refresh/"
        
        try:
            response = self.session.post(
                refresh_url,
                json={"refresh": self.refresh_token},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access')
                
                # Aktualizuje header Authorization
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("✅ Token odświeżony pomyślnie")
                return True
            else:
                logger.error(f"❌ Błąd odświeżania tokena: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Wyjątek podczas odświeżania tokena: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Testuje połączenie z API
        """
        ping_url = f"{self.base_url}/acars/api/ping/"
        
        try:
            response = self.session.get(ping_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Test połączenia: {data.get('message')}")
                logger.info(f"Użytkownik: {data.get('user')}")
                return True
            elif response.status_code == 401:
                logger.warning("⚠️ Token wygasł, próba odświeżenia...")
                if self.refresh_access_token():
                    return self.test_connection()  # Retry
                return False
            else:
                logger.error(f"❌ Błąd testu połączenia: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Wyjątek podczas testu połączenia: {e}")
            return False
    
    def send_acars_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Wysyła wiadomość ACARS do API
        """
        messages_url = f"{self.base_url}/acars/api/messages/"
        
        try:
            response = self.session.post(
                messages_url,
                json=message_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info("✅ Wiadomość ACARS wysłana pomyślnie")
                return True
            elif response.status_code == 401:
                logger.warning("⚠️ Token wygasł, próba odświeżenia...")
                if self.refresh_access_token():
                    return self.send_acars_message(message_data)  # Retry
                return False
            else:
                logger.error(f"❌ Błąd wysyłania wiadomości: {response.status_code}")
                logger.error(f"Odpowiedź: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Wyjątek podczas wysyłania wiadomości: {e}")
            return False
    
    def send_bulk_messages(self, messages: list) -> bool:
        """
        Wysyła wiele wiadomości ACARS jednocześnie
        """
        bulk_url = f"{self.base_url}/acars/api/bulk-create/"
        
        try:
            response = self.session.post(
                bulk_url,
                json=messages,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"✅ Wysłano {data.get('created_count')} wiadomości")
                if data.get('error_count', 0) > 0:
                    logger.warning(f"⚠️ {data.get('error_count')} błędów")
                return True
            elif response.status_code == 401:
                logger.warning("⚠️ Token wygasł, próba odświeżenia...")
                if self.refresh_access_token():
                    return self.send_bulk_messages(messages)  # Retry
                return False
            else:
                logger.error(f"❌ Błąd wysyłania wiadomości zbiorczych: {response.status_code}")
                logger.error(f"Odpowiedź: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Wyjątek podczas wysyłania wiadomości zbiorczych: {e}")
            return False


def create_sample_acars_message() -> Dict[str, Any]:
    """
    Tworzy przykładową wiadomość ACARS z realistycznymi danymi
    """
    return {
        "aircraft_id": "SP-ABC",
        "flight_number": "TS001",
        "route": "EPWA-EGLL",
        "latitude": 52.1657,
        "longitude": 20.9671,
        "altitude": 35000,
        "speed": 480,
        "heading": 270,
        "time_off": "14:30:00",
        "time_on": None,  # Lot w trakcie
        "engine_n1": 85.5,
        "engine_epr": 1.45,
        "fuel_flow": 2850.0,
        "pax_count": 180,
        "cost_index": 25,
        "transmission_mode": "VDL",
        "label": "10",
        "msg_number": 1,
        "direction": "OUT",
        "payload": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulator": "X-Plane 12",
            "aircraft_type": "Boeing 737-800",
            "raw_data": {
                "nav_data": {
                    "nav1_freq": 110.50,
                    "nav2_freq": 108.90
                },
                "weather": {
                    "temperature": -45,
                    "wind_speed": 25,
                    "wind_direction": 280
                }
            }
        }
    }


def simulate_flight_data():
    """
    Symuluje dane lotu i wysyła je okresowo
    """
    client = ACARSClient(API_BASE_URL, USERNAME, PASSWORD)
    
    # Logowanie
    if not client.login():
        logger.error("❌ Nie udało się zalogować")
        return
    
    # Test połączenia
    if not client.test_connection():
        logger.error("❌ Test połączenia nieudany")
        return
    
    # Symulacja wysyłania danych co 30 sekund
    flight_progress = 0
    altitudes = [0, 5000, 15000, 25000, 35000, 35000, 35000, 25000, 15000, 5000, 0]
    
    try:
        for i in range(len(altitudes)):
            message = create_sample_acars_message()
            message["altitude"] = altitudes[i]
            message["latitude"] += (i * 0.1)  # Symulacja ruchu
            message["longitude"] += (i * 0.15)
            
            # Różne fazy lotu
            if i == 0:
                message["time_off"] = datetime.now().strftime("%H:%M:%S")
            elif i == len(altitudes) - 1:
                message["time_on"] = datetime.now().strftime("%H:%M:%S")
            
            if client.send_acars_message(message):
                logger.info(f"📡 Wysłano dane lotu {i+1}/{len(altitudes)}")
            else:
                logger.error(f"❌ Błąd wysyłania danych lotu {i+1}")
            
            if i < len(altitudes) - 1:  # Nie czekaj po ostatniej wiadomości
                time.sleep(30)  # Czekaj 30 sekund
                
    except KeyboardInterrupt:
        logger.info("🛑 Przerwano przez użytkownika")
    except Exception as e:
        logger.error(f"❌ Błąd podczas symulacji: {e}")


def main():
    """
    Główna funkcja demonstracyjna
    """
    print("🚀 Klient ACARS - Demonstracja")
    print("=" * 50)
    
    # Sprawdź czy dane logowania są ustawione
    if USERNAME == "twoja_nazwa_uzytkownika" or PASSWORD == "twoje_haslo":
        print("❌ Ustaw prawidłowe dane logowania w zmiennych USERNAME i PASSWORD")
        return
    
    choice = input("Wybierz opcję:\n1. Test połączenia\n2. Wyślij pojedynczą wiadomość\n3. Symuluj lot\n4. Wyślij wiele wiadomości\nWybór: ")
    
    client = ACARSClient(API_BASE_URL, USERNAME, PASSWORD)
    
    if not client.login():
        return
    
    if choice == "1":
        client.test_connection()
    elif choice == "2":
        message = create_sample_acars_message()
        client.send_acars_message(message)
    elif choice == "3":
        simulate_flight_data()
    elif choice == "4":
        messages = [create_sample_acars_message() for _ in range(5)]
        # Różnicuj wiadomości
        for i, msg in enumerate(messages):
            msg["msg_number"] = i + 1
            msg["latitude"] += i * 0.01
        client.send_bulk_messages(messages)
    else:
        print("❌ Nieprawidłowy wybór")


if __name__ == "__main__":
    main() 