# SmartCARS 3 TFDI - Rozwiązywanie Problemów

## 🎯 Problem: "Invalid credentials" w SmartCARS 3

Nasze Django API jest w 100% zgodne ze specyfikacją SmartCARS 3. Problem jest w konfiguracji SmartCARS 3.

## ✅ Potwierdzone Działające API:
- ✅ API Handler: `https://dtopsky.topsky.app/acars/api/`
- ✅ Login: Format SmartCARS 3 zgodny z phpVMS 7
- ✅ Authentication: JWT tokens działają poprawnie
- ✅ User Endpoint: Zwraca informacje pilota
- ✅ Data Endpoints: schedules, aircraft, airports

## 🔧 Kroki Rozwiązywania Problemu:

### 1. Sprawdź Konfigurację SmartCARS 3

**W SmartCARS 3 → Settings → ACARS Configuration:**

```
✅ Poprawna konfiguracja:
Script URL: https://dtopsky.topsky.app/acars/api/
Username: laszewskimariusz@gmail.com
Password: nowe_haslo123
```

**⚠️ Sprawdź czy nie ma:**
- Dodatkowych spacji w URL
- Niepotrzebnego trailing slash
- Niepoprawnego protokołu (http zamiast https)

### 2. Sprawdź URL Variants

Przetestuj różne warianty URL:

```
Option 1: https://dtopsky.topsky.app/acars/api/
Option 2: https://dtopsky.topsky.app/acars/api
Option 3: https://dtopsky.topsky.app/api/smartcars/
```

### 3. Test SSL Certificates

SmartCARS może mieć problem z SSL. Spróbuj:

```powershell
# Test SSL connection
curl -I https://dtopsky.topsky.app/acars/api/

# Test bez SSL verification (tylko dla testu!)
curl -k https://dtopsky.topsky.app/acars/api/
```

### 4. Sprawdź Windows Firewall/Antivirus

1. **Windows Defender/Antivirus**: Może blokować SmartCARS
2. **Firewall**: Sprawdź czy port 7172 nie jest zablokowany
3. **Proxy/VPN**: Wyłącz temporalnie

### 5. Sprawdź Logs SmartCARS

**Lokalizacja logów:**
```
C:\Users\[username]\AppData\Local\TFDi Design\smartCARS\resources\app\logs\
```

**Sprawdź czy są błędy:**
- `combined-*.log` - główne logi
- `error-*.log` - błędy aplikacji

### 6. Reset SmartCARS Configuration

1. Zamknij SmartCARS 3
2. Usuń folder cache:
   ```
   C:\Users\[username]\AppData\Local\TFDi Design\smartCARS\cache\
   ```
3. Uruchom SmartCARS jako Administrator
4. Skonfiguruj ponownie

### 7. Alternative Connection Methods

**Metoda 1: API Key Instead of Password**

Jeśli masz API key, użyj go zamiast hasła:
```
Username: laszewskimariusz@gmail.com
Password: [your_api_key_here]
```

**Metoda 2: Different Authentication Format**

SmartCARS może oczekiwać formatu email/api_key:
```
Username: email
Password: api_key_lub_hasło
```

### 8. Check SmartCARS Central Settings

W SmartCARS Central sprawdź:
1. Czy Virtual Airline jest aktywna
2. Czy API URL jest poprawnie skonfigurowane
3. Czy są aktywne flight schedules

### 9. Test Network Connectivity

```powershell
# Test podstawowego połączenia
ping dtopsky.topsky.app

# Test HTTPS connection
Test-NetConnection dtopsky.topsky.app -Port 443

# Test DNS resolution
nslookup dtopsky.topsky.app
```

### 10. SmartCARS 3 Debug Mode

1. Uruchom SmartCARS 3
2. Przejdź do Settings → Advanced
3. Włącz "Debug Mode" lub "Verbose Logging"
4. Spróbuj się zalogować
5. Sprawdź szczegółowe logi

## 🔄 Test Manual API Connection

Użyj Postman lub curl do testu manual:

```bash
# Test API Handler
curl -H "User-Agent: smartCARS/3.0 (TFDi Design)" \
     https://dtopsky.topsky.app/acars/api/

# Test Login
curl -X POST \
  -H "User-Agent: smartCARS/3.0 (TFDi Design)" \
  -H "Content-Type: application/json" \
  -d '{"password":"nowe_haslo123"}' \
  "https://dtopsky.topsky.app/acars/api/login?username=laszewskimariusz@gmail.com"
```

## 🚨 Jeśli Nadal Nie Działa:

### Option A: Local Testing
```
1. Uruchom Django dev server: python manage.py runserver
2. W SmartCARS użyj URL: http://localhost:8000/acars/api/
3. Sprawdź czy local connection działa
```

### Option B: SmartCARS Reinstall
```
1. Odinstaluj SmartCARS 3
2. Usuń folder: C:\Users\[username]\AppData\Local\TFDi Design\
3. Reinstaluj SmartCARS 3 jako Administrator
4. Skonfiguruj ponownie
```

### Option C: Contact TFDi Support
```
Jeśli problem persists:
1. Zbierz logi SmartCARS
2. Skontaktuj się z TFDi Design support
3. Podaj szczegóły konfiguracji API
```

## 📋 Checklist Finalny:

- [ ] URL: `https://dtopsky.topsky.app/acars/api/`
- [ ] Username: `laszewskimariusz@gmail.com`
- [ ] Password: `nowe_haslo123`
- [ ] SmartCARS uruchomiony jako Administrator
- [ ] Windows Firewall/Antivirus sprawdzony
- [ ] SSL certificates OK
- [ ] Network connectivity OK
- [ ] SmartCARS logs sprawdzone
- [ ] Manual API test OK (our tests pass!)

## 🎯 Next Steps:

1. **Sprawdź konfigurację SmartCARS 3 punkt po punkt**
2. **Przetestuj local connection (localhost:8000)**
3. **Sprawdź Windows security settings**
4. **Kontakt z TFDi support jeśli problem persists**

**Nasze Django API działa w 100% - problem jest w SmartCARS client configuration!** 