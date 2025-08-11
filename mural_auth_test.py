#!/usr/bin/env python3
"""
Test different Mural API authentication methods
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# Load configuration
with open('lrl-workhorse/mural_config.json', 'r') as f:
    config = json.load(f)

print("Testing Mural API Authentication Methods\n")
print("=" * 60)

# Test endpoints to try
auth_endpoints = [
    "https://api.mural.co/oauth/token",
    "https://api.mural.co/api/public/v1/authorization/oauth2/token",
    "https://app.mural.co/api/public/v1/authorization/oauth2/token",
    "https://app.mural.co/oauth/token",
]

# OAuth2 client credentials
client_id = config['oauth']['client_id']
client_secret = config['oauth']['client_secret']

print(f"Client ID: {client_id[:10]}...")
print(f"Client Secret: {client_secret[:10]}...")
print()

# Test different OAuth endpoints
for endpoint in auth_endpoints:
    print(f"\nTrying endpoint: {endpoint}")
    print("-" * 40)
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'murals:read murals:write'
    }
    
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    
    request = urllib.request.Request(
        endpoint,
        data=encoded_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST'
    )
    
    try:
        # Create SSL context that doesn't verify certificates (for testing)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(request, context=ctx) as response:
            if response.status == 200:
                token_data = json.loads(response.read().decode('utf-8'))
                access_token = token_data.get('access_token')
                print(f"✓ SUCCESS! Got access token: {access_token[:20]}...")
                print(f"Token type: {token_data.get('token_type')}")
                print(f"Expires in: {token_data.get('expires_in')} seconds")
                
                # Save working endpoint
                print(f"\n🎯 WORKING ENDPOINT: {endpoint}")
                
                # Test the token with a simple API call
                test_url = f"https://api.mural.co/api/v0/murals/{config['workspace_id']}.{config['board_id']}"
                test_request = urllib.request.Request(
                    test_url,
                    headers={'Authorization': f'Bearer {access_token}'},
                    method='GET'
                )
                
                try:
                    with urllib.request.urlopen(test_request, context=ctx) as test_response:
                        if test_response.status == 200:
                            print(f"✓ Token works! Can access board {config['board_id']}")
                        else:
                            print(f"⚠️ Token received but board access failed: {test_response.status}")
                except Exception as e:
                    print(f"⚠️ Token test failed: {e}")
                
                break
            else:
                print(f"✗ Unexpected status: {response.status}")
                
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            # Only print first 200 chars of error
            if len(error_body) > 200:
                print(f"   Response: {error_body[:200]}...")
            else:
                print(f"   Response: {error_body}")
        except:
            pass
            
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("\nAlternative: Try using a personal access token")
print("1. Log into Mural at https://app.mural.co")
print("2. Go to your profile settings")
print("3. Look for 'Developer' or 'API' section")
print("4. Generate a personal access token")
print("5. Use that token directly with 'Bearer' authorization")
