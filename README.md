# dtop-acars

Django project for ACARS (Aircraft Communications Addressing and Reporting System) management.

## Setup Instructions

### Prerequisites
- Python 3.13+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dtop-acars
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file with your settings
   # Make sure to set a secure SECRET_KEY
   ```

5. **Run Django migrations**
   ```bash
   cd topsky
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   The application will be available at http://127.0.0.1:8000/

## Environment Variables

Create a `.env` file in the root directory with the following variables:

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to 'True' for development, 'False' for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Project Structure

```
dtop-acars/
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── venv/              # Virtual environment
└── topsky/            # Django project
    ├── manage.py      # Django management script
    ├── db.sqlite3     # SQLite database
    └── topsky/        # Django project settings
        ├── __init__.py
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
        └── asgi.py
```

## Security Notes

- Never commit the `.env` file to version control
- Keep your `SECRET_KEY` secure and unique
- Use different settings for development and production environments

## Development

- The project uses Django 5.2.3
- SQLite database for development
- Virtual environment for dependency isolation