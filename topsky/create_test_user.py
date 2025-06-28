#!/usr/bin/env python3
"""
Skrypt do stworzenia użytkownika testowego
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topsky.settings')
django.setup()

from django.contrib.auth.models import User

# Usuń istniejącego użytkownika testowego
User.objects.filter(username='testuser').delete()

# Stwórz nowego użytkownika testowego
user = User.objects.create_user(
    username='testuser',
    email='test@example.com', 
    password='testpassword'
)

print(f"✅ Stworzony użytkownik testowy:")
print(f"   Username: {user.username}")
print(f"   Email: {user.email}")
print(f"   ID: {user.id}")

# Sprawdź czy użytkownik Zatto istnieje
try:
    zatto = User.objects.get(username='Zatto')
    print(f"\n✅ Znaleziony użytkownik Zatto:")
    print(f"   Username: {zatto.username}")
    print(f"   Email: {zatto.email}")
    print(f"   ID: {zatto.id}")
except User.DoesNotExist:
    print(f"\n⚠️ Użytkownik Zatto nie istnieje - stworzę go...")
    zatto = User.objects.create_user(
        username='Zatto',
        email='zatto@topsky.app',
        password='nowe_haslo123'
    )
    print(f"   Stworzony Zatto: {zatto.username} ({zatto.email})") 