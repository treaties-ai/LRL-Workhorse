#!/usr/bin/env python3
"""
Simple Mural API test using OAuth client credentials
Creates sticky notes on the existing board
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Configuration
CLIENT_ID = os.getenv('MURAL_CLIENT_ID')
CLIENT_SECRET = os.getenv('MURAL_CLIENT_SECRET')
WORKSPACE_ID = "root7380"
BOARD_ID = "1754493659737"
BASE_URL = "https://api.mural.co/api/public/v1"

print("\n" + "="*60)
print("SIMPLE MURAL API TEST - OAUTH AUTHENTICATION")
print("="*60)

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ No OAuth credentials found in .env file")
    exit(1)

print(f"✓ Client ID loaded: {CLIENT_ID[:10]}...")
print(f"✓ Workspace: {WORKSPACE_ID}")
print(f"✓ Board ID: {BOARD_ID}")

# Get OAuth token
def get_oauth_token():
    """Get OAuth access token using client credentials"""
    oauth_endpoints = [
        "https://app.mural.co/api/public/v1/authorization/oauth2/token",
        "https://api.mural.co/api/public/v1/authorization/oauth2/token",
        "https://api.mural.co/oauth2/token"
    ]
    
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "murals:read murals:write"
    }
    
    for endpoint in oauth_endpoints:
        try:
            print(f"Trying OAuth endpoint: {endpoint}")
            response = requests.post(endpoint, data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                print(f"✓ OAuth successful!")
                return token_data.get('access_token')
            else:
                print(f"  Failed ({response.status_code}): {response.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")
    
    return None

# Get token
print("\n--- Getting OAuth Token ---")
access_token = get_oauth_token()

if not access_token:
    print("❌ Failed to get OAuth token")
    exit(1)

print(f"✓ Access token obtained: {access_token[:20]}...")

# Set up headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Board URL for reference
board_url = f"https://app.mural.co/t/{WORKSPACE_ID}/m/{WORKSPACE_ID}/{BOARD_ID}"
print(f"\n🌐 Board URL: {board_url}")

def create_sticky_note(text, x, y, color="#FFFF00"):
    """Create a sticky note on the Mural board"""
    endpoint = f"{BASE_URL}/murals/{BOARD_ID}/widgets/sticky-note"
    
    data = {
        "text": text,
        "x": x,
        "y": y,
        "width": 110,
        "height": 110,
        "style": {
            "backgroundColor": color,
            "fontSize": 14
        }
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"  ✓ Created: {text[:30]}")
            return True
        else:
            print(f"  ✗ Failed ({response.status_code}): {text[:30]}")
            print(f"    Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

print("\n--- Creating Body Visualization ---")

# Body parts with coordinates
body_parts = [
    {"text": "HEAD", "x": 400, "y": 100, "color": "#E0E0E0"},
    {"text": "HEART ♥", "x": 390, "y": 200, "color": "#FF6B6B"},
    {"text": "TORSO", "x": 400, "y": 300, "color": "#E0E0E0"},
    {"text": "L-ARM", "x": 250, "y": 250, "color": "#E0E0E0"},
    {"text": "R-ARM", "x": 550, "y": 250, "color": "#E0E0E0"},
    {"text": "L-LEG", "x": 350, "y": 400, "color": "#E0E0E0"},
    {"text": "R-LEG", "x": 450, "y": 400, "color": "#E0E0E0"}
]

created_count = 0
for part in body_parts:
    if create_sticky_note(part["text"], part["x"], part["y"], part["color"]):
        created_count += 1
    time.sleep(0.5)  # Small delay between API calls

print(f"\nBody visualization: {created_count}/{len(body_parts)} parts created")

print("\n--- Creating Somatic Mapping Notes ---")

# Somatic notes with TDAI scoring
somatic_notes = [
    {
        "text": "Deep grief in chest - TDAI 8.5",
        "x": 390,
        "y": 230,
        "color": "#2ECC71"  # Deep green for high TDAI
    },
    {
        "text": "Racing thoughts - TDAI 6.0",
        "x": 400,
        "y": 130,
        "color": "#6BCF7F"  # Light green
    },
    {
        "text": "Grounded feeling - TDAI 7.5",
        "x": 350,
        "y": 430,
        "color": "#2ECC71"  # Deep green
    }
]

somatic_count = 0
for note in somatic_notes:
    if create_sticky_note(note["text"], note["x"], note["y"], note["color"]):
        somatic_count += 1
    time.sleep(0.5)

print(f"\nSomatic mapping: {somatic_count}/{len(somatic_notes)} notes created")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
total_created = created_count + somatic_count
total_attempted = len(body_parts) + len(somatic_notes)
success_rate = (total_created / total_attempted * 100) if total_attempted > 0 else 0

print(f"Total sticky notes created: {total_created}/{total_attempted}")
print(f"Success rate: {success_rate:.1f}%")
print(f"\n🎯 Check your Mural board at:")
print(f"   {board_url}")
print("\nThe board should now show:")
print("  • Body visualization (head, torso, arms, legs)")
print("  • Somatic mapping notes with TDAI color coding")
print("="*60)

if total_created > 0:
    print("\n✅ Test completed successfully!")
else:
    print("\n❌ Test failed - check API key and permissions")
