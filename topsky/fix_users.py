#!/usr/bin/env python3
"""
Script to fix user accounts - remove duplicates and set admin rights
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topsky.settings')
django.setup()

from django.contrib.auth.models import User
from acars.models import SmartcarsProfile

def fix_users():
    print("=== Fixing User Accounts ===")
    
    # Show current users
    print("\nCurrent users:")
    for user in User.objects.all():
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")
    
    # Remove mariu user
    try:
        mariu = User.objects.get(username='mariu')
        print(f"\nRemoving user: {mariu.username} (ID: {mariu.id})")
        mariu.delete()
        print("✅ User 'mariu' deleted")
    except User.DoesNotExist:
        print("ℹ️ User 'mariu' not found")
    
    # Make Zatto admin
    try:
        zatto = User.objects.get(username='Zatto')
        print(f"\nMaking Zatto an admin...")
        zatto.is_staff = True
        zatto.is_superuser = True
        zatto.save()
        print("✅ Zatto is now a superuser")
        
        # Create or get SmartCARS profile for Zatto
        profile = SmartcarsProfile.get_or_create_for_user(zatto)
        print(f"✅ SmartCARS profile for Zatto: API Key = {profile.api_key}")
        
    except User.DoesNotExist:
        print("❌ User 'Zatto' not found")
    
    print("\n=== Final user list ===")
    for user in User.objects.all():
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")
        
        # Show SmartCARS profile if exists
        try:
            profile = user.smartcars_profile
            print(f"   SmartCARS API Key: {profile.api_key}")
        except SmartcarsProfile.DoesNotExist:
            print("   No SmartCARS profile")

if __name__ == "__main__":
    fix_users() 