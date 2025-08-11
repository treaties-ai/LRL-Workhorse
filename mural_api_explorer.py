#!/usr/bin/env python3
"""
MURAL API Explorer - Systematically test all possible endpoints to find the correct widget creation API
"""

import requests
import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('.env')

ACCESS_TOKEN = os.getenv('MURAL_ACCESS_TOKEN')
REFRESH_TOKEN = os.getenv('MURAL_REFRESH_TOKEN')
CLIENT_ID = os.getenv('MURAL_CLIENT_ID')
CLIENT_SECRET = os.getenv('MURAL_CLIENT_SECRET')
WORKSPACE_ID = "root7380"
BOARD_ID = "1754493659737"

print("\n" + "="*70)
print("MURAL API EXPLORER - FINDING THE CORRECT WIDGET CREATION ENDPOINT")
print("="*70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Workspace: {WORKSPACE_ID}")
print(f"Board ID: {BOARD_ID}")
print(f"Token: {ACCESS_TOKEN[:30]}..." if ACCESS_TOKEN else "NO TOKEN FOUND")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_token_validity():
    """Verify the access token is valid"""
    print("\n" + "-"*60)
    print("STEP 1: Verifying Token Validity")
    print("-"*60)
    
    test_endpoints = [
        ("User Info", "https://app.mural.co/api/public/v1/users/me"),
        ("Workspaces", "https://app.mural.co/api/public/v1/workspaces"),
    ]
    
    for name, endpoint in test_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Token is valid (200 OK)")
                data = response.json()
                if name == "User Info" and 'email' in data:
                    print(f"   User: {data.get('email', 'Unknown')}")
                elif name == "Workspaces" and 'value' in data:
                    print(f"   Found {len(data['value'])} workspace(s)")
            elif response.status_code == 401:
                print(f"❌ {name}: Token expired or invalid (401)")
                return False
            else:
                print(f"⚠️ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"💥 {name}: Error - {str(e)}")
            return False
    
    return True

def test_mural_access():
    """Test if we can access the specific mural/board"""
    print("\n" + "-"*60)
    print("STEP 2: Testing Mural/Board Access")
    print("-"*60)
    
    mural_endpoints = [
        (f"Mural by ID", f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}"),
        (f"Mural Combined", f"https://app.mural.co/api/public/v1/murals/{WORKSPACE_ID}.{BOARD_ID}"),
        (f"Board by ID", f"https://app.mural.co/api/public/v1/boards/{BOARD_ID}"),
    ]
    
    for name, endpoint in mural_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"\n{name}:")
            print(f"  Endpoint: {endpoint}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS - Can access this mural/board!")
                data = response.json()
                if 'title' in data:
                    print(f"  Title: {data.get('title', 'Unknown')}")
                if 'id' in data:
                    print(f"  ID Format: {data.get('id')}")
                return endpoint  # Return the working endpoint
            elif response.status_code == 404:
                print(f"  ❌ Not found")
            elif response.status_code == 403:
                print(f"  ⚠️ Permission denied")
            else:
                print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"  💥 Error: {str(e)}")
    
    return None

def test_widget_endpoints():
    """Test all possible widget creation endpoints"""
    print("\n" + "-"*60)
    print("STEP 3: Testing Widget Creation Endpoints")
    print("-"*60)
    
    # Minimal widget payload for testing
    widget_data = {
        "type": "sticky-note",
        "text": "API Explorer Test",
        "x": 100,
        "y": 100,
        "style": {
            "backgroundColor": "#FFFF00"
        }
    }
    
    # Alternative payload formats to try
    alternative_payloads = [
        # Format 1: Standard
        widget_data,
        
        # Format 2: With content wrapper
        {
            "type": "sticky-note",
            "content": {
                "text": "API Explorer Test"
            },
            "position": {
                "x": 100,
                "y": 100
            },
            "style": {
                "backgroundColor": "#FFFF00"
            }
        },
        
        # Format 3: Minimal
        {
            "text": "API Explorer Test",
            "x": 100,
            "y": 100
        },
        
        # Format 4: With shape property
        {
            "shape": "sticky-note",
            "text": "API Explorer Test",
            "x": 100,
            "y": 100,
            "backgroundColor": "#FFFF00"
        }
    ]
    
    # Test endpoints in priority order based on OAuth success pattern
    endpoints_to_test = [
        # Priority 1: Public v1 API (matches successful OAuth endpoints)
        f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets",
        f"https://app.mural.co/api/public/v1/murals/{WORKSPACE_ID}.{BOARD_ID}/widgets",
        f"https://app.mural.co/api/public/v1/boards/{BOARD_ID}/widgets",
        
        # Priority 2: Public v1 with specific widget types
        f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/sticky-note",
        f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/sticky-notes",
        f"https://app.mural.co/api/public/v1/boards/{BOARD_ID}/sticky-notes",
        
        # Priority 3: V0 API variations (current implementation attempts)
        f"https://api.mural.co/api/v0/murals/{WORKSPACE_ID}.{BOARD_ID}/widgets",
        f"https://api.mural.co/api/v0/murals/{BOARD_ID}/widgets",
        f"https://api.mural.co/api/v0/boards/{BOARD_ID}/widgets",
        
        # Priority 4: Alternative domain patterns
        f"https://api.mural.co/api/public/v1/murals/{BOARD_ID}/widgets",
        f"https://app.mural.co/api/v1/murals/{BOARD_ID}/widgets",
        f"https://app.mural.co/api/v1/boards/{BOARD_ID}/widgets",
        
        # Priority 5: Batch endpoints
        f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/batch",
        f"https://app.mural.co/api/public/v1/boards/{BOARD_ID}/widgets/batch",
    ]
    
    print(f"\nTesting {len(endpoints_to_test)} endpoints with {len(alternative_payloads)} payload formats...")
    print("="*70)
    
    successful_combinations = []
    
    for endpoint_idx, endpoint in enumerate(endpoints_to_test, 1):
        print(f"\n[{endpoint_idx}/{len(endpoints_to_test)}] Testing: {endpoint}")
        
        for payload_idx, payload in enumerate(alternative_payloads, 1):
            try:
                # For batch endpoints, wrap payload in widgets array
                if "batch" in endpoint:
                    test_payload = {"widgets": [payload]}
                else:
                    test_payload = payload
                
                response = requests.post(
                    endpoint, 
                    headers=headers, 
                    json=test_payload, 
                    timeout=10
                )
                
                status = response.status_code
                
                if status in [200, 201]:
                    print(f"  ✅ SUCCESS with payload format {payload_idx}!")
                    print(f"     Status: {status}")
                    print(f"     Response: {response.text[:200]}")
                    successful_combinations.append({
                        "endpoint": endpoint,
                        "payload_format": payload_idx,
                        "payload": test_payload,
                        "response": response.json()
                    })
                    
                    # Save the successful configuration
                    with open('mural_working_endpoint.json', 'w') as f:
                        json.dump({
                            "endpoint": endpoint,
                            "payload_format": payload_idx,
                            "example_payload": test_payload,
                            "timestamp": datetime.now().isoformat()
                        }, f, indent=2)
                    
                    return endpoint, test_payload
                    
                elif status == 404 and payload_idx == 1:
                    print(f"  ❌ 404 - Endpoint not found")
                    break  # No need to try other payloads if endpoint doesn't exist
                    
                elif status == 400 and payload_idx < len(alternative_payloads):
                    continue  # Try next payload format
                    
                elif status == 401:
                    print(f"  ⚠️ 401 - Authentication failed (token may have expired)")
                    break
                    
                elif status == 403:
                    print(f"  ⚠️ 403 - Permission denied")
                    break
                    
                elif payload_idx == len(alternative_payloads):
                    # Last payload format, show the error
                    print(f"  Status {status}: {response.text[:100]}")
                    
            except requests.exceptions.Timeout:
                print(f"  ⏱️ Timeout after 10 seconds")
                break
            except Exception as e:
                if payload_idx == len(alternative_payloads):
                    print(f"  💥 Error: {str(e)}")
            
            # Small delay between attempts to avoid rate limiting
            time.sleep(0.2)
    
    return None, None

def test_alternative_methods():
    """Test alternative methods like GET to understand API structure"""
    print("\n" + "-"*60)
    print("STEP 4: Testing Alternative Methods (GET widgets)")
    print("-"*60)
    
    get_endpoints = [
        f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets",
        f"https://app.mural.co/api/public/v1/boards/{BOARD_ID}/widgets",
        f"https://api.mural.co/api/v0/murals/{BOARD_ID}/widgets",
    ]
    
    for endpoint in get_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"\nGET {endpoint}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Can GET widgets from this endpoint!")
                data = response.json()
                if isinstance(data, list):
                    print(f"  Found {len(data)} existing widgets")
                elif 'value' in data:
                    print(f"  Found {len(data['value'])} existing widgets")
                # If GET works, POST might work with correct format
                return endpoint
                
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    return None

def refresh_access_token():
    """Attempt to refresh the access token"""
    print("\n" + "-"*60)
    print("OPTIONAL: Refreshing Access Token")
    print("-"*60)
    
    if not REFRESH_TOKEN:
        print("❌ No refresh token available")
        return None
    
    refresh_url = "https://app.mural.co/api/public/v1/authorization/oauth2/token/"
    refresh_data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(refresh_url, data=refresh_data, timeout=10)
        if response.status_code == 200:
            token_info = response.json()
            new_token = token_info.get('access_token')
            print(f"✅ Token refreshed successfully!")
            print(f"   New token: {new_token[:30]}...")
            
            # Update .env file
            with open('.env', 'r') as f:
                lines = f.readlines()
            
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('MURAL_ACCESS_TOKEN='):
                        f.write(f'MURAL_ACCESS_TOKEN={new_token}\n')
                    else:
                        f.write(line)
            
            return new_token
        else:
            print(f"❌ Refresh failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"💥 Refresh error: {str(e)}")
    
    return None

# Main execution
if __name__ == "__main__":
    # Step 1: Verify token
    if not test_token_validity():
        print("\n⚠️ Token validation failed. Attempting to refresh...")
        new_token = refresh_access_token()
        if new_token:
            ACCESS_TOKEN = new_token
            headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
            if not test_token_validity():
                print("\n❌ Token still invalid after refresh. Please run mural_oauth_setup.py")
                exit(1)
        else:
            print("\n❌ Could not refresh token. Please run mural_oauth_setup.py")
            exit(1)
    
    # Step 2: Test mural access
    working_mural_endpoint = test_mural_access()
    if working_mural_endpoint:
        print(f"\n✅ Found working mural endpoint: {working_mural_endpoint}")
    
    # Step 3: Test widget creation
    working_endpoint, working_payload = test_widget_endpoints()
    
    # Step 4: If no POST works, try GET to understand structure
    if not working_endpoint:
        get_endpoint = test_alternative_methods()
        if get_endpoint:
            print(f"\n💡 GET works on {get_endpoint}, but POST might need different format")
    
    # Summary
    print("\n" + "="*70)
    print("EXPLORATION SUMMARY")
    print("="*70)
    
    if working_endpoint:
        print("✅ SUCCESS! Found working widget creation endpoint!")
        print(f"   Endpoint: {working_endpoint}")
        print(f"   Payload format saved to: mural_working_endpoint.json")
        print("\nNext steps:")
        print("1. Update MURAL_BEST_PRACTICES.md with the working endpoint")
        print("2. Update all test files to use this endpoint")
        print("3. Run your tests to create widgets on the board")
    else:
        print("❌ No working widget creation endpoint found")
        print("\nPossible issues:")
        print("1. API endpoints may have changed - check MURAL's latest documentation")
        print("2. Token might not have correct scopes - regenerate with 'murals:write' scope")
        print("3. Board permissions - ensure your OAuth app has access to this workspace")
        print("\nRecommended actions:")
        print("1. Check MURAL's developer portal for updated API documentation")
        print("2. Try using MURAL's API sandbox/playground if available")
        print("3. Contact MURAL support with the specific board ID and error details")
