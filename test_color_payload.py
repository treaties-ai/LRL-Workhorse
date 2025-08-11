#!/usr/bin/env python3
"""
Test different payload formats for coloring widgets
The endpoint exists but the payload structure is wrong
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')

ACCESS_TOKEN = os.getenv('MURAL_ACCESS_TOKEN')
BOARD_ID = os.getenv('MURAL_BOARD_ID', 'root7380.1754493659737')

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Test widget ID from the previous run
test_widget_id = "a320d6fc-222a-4e20-93c9-4c9e6ed81590"

# The endpoint that gave us 400 (not 404)
endpoint = f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/sticky-note/{test_widget_id}"

print("Testing different payload formats for coloring widgets...")
print("="*60)
print(f"Endpoint: {endpoint}")
print("="*60)

# Test different payload formats
payloads_to_test = [
    # Format 1: Original attempt
    {
        "style": {
            "backgroundColor": "#FF0000"
        }
    },
    
    # Format 2: Direct backgroundColor
    {
        "backgroundColor": "#FF0000"
    },
    
    # Format 3: Color without hash
    {
        "style": {
            "backgroundColor": "FF0000"
        }
    },
    
    # Format 4: RGB format
    {
        "style": {
            "backgroundColor": "rgb(255, 0, 0)"
        }
    },
    
    # Format 5: Color name
    {
        "style": {
            "backgroundColor": "red"
        }
    },
    
    # Format 6: Style as string
    {
        "style": "backgroundColor:#FF0000"
    },
    
    # Format 7: Fill instead of backgroundColor
    {
        "style": {
            "fill": "#FF0000"
        }
    },
    
    # Format 8: Direct fill
    {
        "fill": "#FF0000"
    },
    
    # Format 9: Properties object
    {
        "properties": {
            "backgroundColor": "#FF0000"
        }
    },
    
    # Format 10: Update wrapper
    {
        "update": {
            "style": {
                "backgroundColor": "#FF0000"
            }
        }
    }
]

for i, payload in enumerate(payloads_to_test, 1):
    print(f"\nTest {i}: {str(payload)[:80]}...")
    
    try:
        response = requests.patch(
            endpoint,
            headers=headers,
            json=payload,
            timeout=5
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print(f"  ✅ SUCCESS! This payload format works!")
            print(f"  Payload: {payload}")
            print(f"  Response: {response.text[:200] if response.text else 'Empty (204)'}")
            break
        elif response.status_code == 400:
            print(f"  ❌ Bad Request")
            if response.text:
                # Parse the error to understand what's expected
                print(f"  Error: {response.text[:200]}")
        else:
            print(f"  ❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"  💥 Exception: {str(e)}")

print("\n" + "="*60)
print("\nConclusion:")
print("If none of the payloads worked, the API might not support color updates")
print("or requires a completely different approach (e.g., delete and recreate)")
