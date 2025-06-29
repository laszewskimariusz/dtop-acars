#!/usr/bin/env python3
"""
Debug script for ACARS SmartCARS API
Run with: python manage.py runscript debug_acars
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topsky.settings')
django.setup()

from django.contrib.auth.models import User
from acars.models import SmartcarsProfile
from acars.authentication import authenticate_smartcars_user
import json

def debug_users():
    """Debug user accounts"""
    print("=== DEBUG: Users ===")
    users = User.objects.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
def debug_smartcars_profiles():
    """Debug SmartCARS profiles"""
    print("\n=== DEBUG: SmartCARS Profiles ===")
    profiles = SmartcarsProfile.objects.all()
    for profile in profiles:
        print(f"User: {profile.user.username}, API Key: {profile.api_key[:10]}..., ACARS Token: {profile.acars_token[:10]}...")

def create_test_user():
    """Create a clean test user"""
    print("\n=== Creating Test User ===")
    
    # Remove existing test users
    User.objects.filter(email="test@topsky.app").delete()
    User.objects.filter(username="testpilot").delete()
    
    # Create new test user
    user = User.objects.create_user(
        username="testpilot",
        email="test@topsky.app",
        password="testpassword123",
        first_name="Test",
        last_name="Pilot"
    )
    
    print(f"Created user: {user.username} ({user.email})")
    
    # Create SmartCARS profile
    profile = SmartcarsProfile.get_or_create_for_user(user)
    print(f"Created SmartCARS profile with API key: {profile.api_key}")
    
    return user

def test_authentication():
    """Test authentication methods"""
    print("\n=== Testing Authentication ===")
    
    # Test with test user
    test_email = "test@topsky.app"
    test_password = "testpassword123"
    
    print(f"Testing login: {test_email} / {test_password}")
    
    # Test regular authentication
    user = authenticate_smartcars_user(test_email, test_password)
    print(f"Password auth result: {user}")
    
    if user:
        # Test API key authentication
        try:
            profile = user.smartcars_profile
            api_key = profile.api_key
            print(f"Testing API key auth: {test_email} / {api_key[:10]}...")
            
            api_user = authenticate_smartcars_user(test_email, api_key)
            print(f"API key auth result: {api_user}")
            
        except SmartcarsProfile.DoesNotExist:
            print("No SmartCARS profile found")

def test_login_endpoint():
    """Test the actual login endpoint"""
    print("\n=== Testing Login Endpoint ===")
    
    from django.test import Client
    from django.urls import reverse
    import json
    
    client = Client()
    
    # Test data
    login_data = {
        "email": "test@topsky.app",
        "password": "testpassword123"
    }
    
    # Test POST to login endpoint
    try:
        response = client.post(
            '/api/smartcars/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if hasattr(response, 'json'):
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response content: {response.content.decode()}")
            
    except Exception as e:
        print(f"Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("ACARS Debug Script")
    print("=" * 50)
    
    debug_users()
    debug_smartcars_profiles()
    
    # Create clean test user
    test_user = create_test_user()
    
    # Test authentication
    test_authentication()
    
    # Test actual endpoint
    test_login_endpoint()
    
    print("\n=== Summary ===")
    print("✅ Debug completed!")
    print("Now you can test with:")
    print("Email: test@topsky.app")
    print("Password: testpassword123")

if __name__ == "__main__":
    main() 