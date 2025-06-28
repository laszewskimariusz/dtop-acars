#!/usr/bin/env python3
"""
Test script for SmartCARS 3 API debugging
This script generates curl commands to test the SmartCARS authentication flow
"""

import argparse
import sys

def generate_debug_curl_command(base_url, email, api_key, content_type="application/x-www-form-urlencoded"):
    """Generate curl command for debugging SmartCARS login"""
    
    if content_type == "application/json":
        data_flag = "-d"
        data_content = f'{{"email":"{email}","api_key":"{api_key}"}}'
    else:
        data_flag = "--data-urlencode"
        data_content = f'"email={email}" --data-urlencode "api_key={api_key}"'
    
    return f"""curl -v -X POST "{base_url}/acars/api/login?debug=1" \\
     -H "Content-Type: {content_type}" \\
     {data_flag} {data_content}"""

def generate_test_login_command(base_url, email, api_key, content_type="application/x-www-form-urlencoded"):
    """Generate curl command for actual SmartCARS login test"""
    
    if content_type == "application/json":
        data_flag = "-d"
        data_content = f'{{"email":"{email}","api_key":"{api_key}"}}'
    else:
        data_flag = "--data-urlencode"
        data_content = f'"email={email}" --data-urlencode "api_key={api_key}"'
    
    return f"""curl -v -X POST "{base_url}/acars/api/login" \\
     -H "Content-Type: {content_type}" \\
     {data_flag} {data_content}"""

def main():
    parser = argparse.ArgumentParser(description='Generate SmartCARS 3 API test commands')
    parser.add_argument('--email', required=True, help='User email address')
    parser.add_argument('--api-key', required=True, help='SmartCARS API key')
    parser.add_argument('--base-url', default='https://dtopsky.topsky.app', help='Base URL of the API')
    parser.add_argument('--json', action='store_true', help='Use JSON format instead of form data')
    
    args = parser.parse_args()
    
    content_type = "application/json" if args.json else "application/x-www-form-urlencoded"
    
    print("🔍 SmartCARS 3 API Debug Test Commands")
    print("=" * 50)
    print()
    
    print("1️⃣  DEBUG MODE - See what data is being received:")
    print(generate_debug_curl_command(args.base_url, args.email, args.api_key, content_type))
    print()
    
    print("2️⃣  NORMAL LOGIN - Test actual authentication:")
    print(generate_test_login_command(args.base_url, args.email, args.api_key, content_type))
    print()
    
    print("3️⃣  DEBUG WITH ALTERNATIVE FIELD NAMES:")
    if content_type == "application/json":
        alt_data = f'{{"username":"{args.email}","password":"{args.api_key}"}}'
    else:
        alt_data = f'"username={args.email}" --data-urlencode "password={args.api_key}"'
    
    print(f"""curl -v -X POST "{args.base_url}/acars/api/login?debug=1" \\
     -H "Content-Type: {content_type}" \\
     {"--data-urlencode" if content_type != "application/json" else "-d"} {alt_data}""")
    print()
    
    print("4️⃣  TEST WITH OTHER FIELD VARIATIONS:")
    variations = [
        ('user', 'pass'),
        ('login', 'pwd'),
        ('pilot_id', 'secret')
    ]
    
    for user_field, pass_field in variations:
        if content_type == "application/json":
            var_data = f'{{"{user_field}":"{args.email}","{pass_field}":"{args.api_key}"}}'
        else:
            var_data = f'"{user_field}={args.email}" --data-urlencode "{pass_field}={args.api_key}"'
        
        print(f"""curl -v -X POST "{args.base_url}/acars/api/login?debug=1" \\
     -H "Content-Type: {content_type}" \\
     {"--data-urlencode" if content_type != "application/json" else "-d"} {var_data}""")
        print()
    
    print("📋 Expected Debug Response Structure:")
    print("""
{
    "debug_info": {
        "content_type": "application/x-www-form-urlencoded",
        "method": "POST",
        "POST_data": {...},
        "JSON_data": {...},
        "query_params": {"debug": "1"},
        "headers": {...},
        "body": "...",
        "extracted_fields": {
            "email": "your_email@example.com",
            "api_key": "your_api_key",
            "basic_auth_found": false
        }
    }
}
""")
    
    print("✅ Expected Successful Login Response:")
    print("""
{
    "status": "success",
    "message": "Login successful",
    "data": {
        "pilot_id": 123,
        "api_key": "<JWT_TOKEN>",
        "refresh_token": "<REFRESH_TOKEN>",
        "user": {
            "name": "User Name",
            "email": "user@example.com"
        }
    }
}
""")
    
    print("❌ Expected Error Response:")
    print("""
{
    "status": "error",
    "message": "Invalid credentials"
}
""")

if __name__ == '__main__':
    main() 