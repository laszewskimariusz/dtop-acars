# Konfiguracja Bazy Danych PostgreSQL

## Instalacja Dependencies

Wszystkie wymagane pakiety zostały już dodane do `requirements.txt`. Zainstaluj je:

```bash
pip install -r requirements.txt
```

## Konfiguracja Środowiska

### 1. Skopiuj przykładowy plik środowiskowy:
```bash
cp .env.example .env
```

### 2. Edytuj `.env` i ustaw `DATABASE_URL`:

**Dla lokalnej PostgreSQL:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/dtop_acars
```

**Dla produkcji (np. Railway, Supabase):**
```
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require
```

**Dla lokalnego rozwoju (SQLite):**
Pozostaw `DATABASE_URL` zakomentowane - aplikacja automatycznie użyje SQLite.

## Migracje Bazy Danych

### 1. Stwórz migracje:
```bash
cd topsky
python manage.py makemigrations
```

### 2. Zastosuj migracje:
```bash
python manage.py migrate
```

### 3. Stwórz superużytkownika (opcjonalnie):
```bash
python manage.py createsuperuser
```

## Uruchomienie Aplikacji

```bash
cd topsky
python manage.py runserver
```

## Deployment

### GitHub Secrets

W GitHub repository dodaj następujące sekrety:

- `SECRET_KEY` - klucz Django
- `ALLOWED_HOSTS` - dozwolone hosty (oddzielone przecinkami)
- `DATABASE_URL` - URL bazy danych PostgreSQL
- `HARBOR_USERNAME` - nazwa użytkownika Harbor
- `HARBOR_PASSWORD` - hasło Harbor
- `GH_PAT` - Personal Access Token GitHub
- `KUBECONFIG` - konfiguracja kubectl

### Automatyczny Deploy

Deploy uruchamia się automatycznie przy tagowaniu wersji:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Sprawdzanie Konfiguracji

Aplikacja automatycznie wybiera bazę danych na podstawie zmiennej `DATABASE_URL`:

- **Jeśli `DATABASE_URL` jest ustawione** → PostgreSQL
- **Jeśli `DATABASE_URL` nie jest ustawione** → SQLite (fallback)

To umożliwia łatwe przełączanie między bazami podczas rozwoju i produkcji. 