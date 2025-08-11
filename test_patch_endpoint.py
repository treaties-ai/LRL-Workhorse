#!/usr/bin/env python3
"""
Test different PATCH endpoint formats to find the correct one for coloring widgets
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

# Color payload
color_payload = {
    "style": {
        "backgroundColor": "#FF0000"
    }
}

print("Testing different PATCH endpoint formats...")
print("="*60)

# Test different endpoint formats
endpoints_to_test = [
    # Format 1: With /widgets/ in path
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/{test_widget_id}",
    
    # Format 2: With /widgets/sticky-note/ in path
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/sticky-note/{test_widget_id}",
    
    # Format 3: Without board ID, just widget
    f"https://app.mural.co/api/public/v1/widgets/{test_widget_id}",
    
    # Format 4: Different structure
    f"https://app.mural.co/api/public/v1/widgets/sticky-note/{test_widget_id}",
    
    # Format 5: Update endpoint
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/sticky-notes/{test_widget_id}",
]

for i, endpoint in enumerate(endpoints_to_test, 1):
    print(f"\nTest {i}: {endpoint}")
    
    try:
        response = requests.patch(
            endpoint,
            headers=headers,
            json=color_payload,
            timeout=5
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print(f"  ✅ SUCCESS! This endpoint format works!")
            print(f"  Response: {response.text[:200] if response.text else 'Empty (204)'}")
            break
        else:
            print(f"  ❌ Failed")
            if response.text:
                print(f"  Error: {response.text[:150]}")
    except Exception as e:
        print(f"  💥 Exception: {str(e)}")

print("\n" + "="*60)

# Also try a PUT request instead of PATCH
print("\nTrying PUT instead of PATCH...")
put_endpoint = f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/{test_widget_id}"

try:
    response = requests.put(
        put_endpoint,
        headers=headers,
        json=color_payload,
        timeout=5
    )
    
    print(f"PUT Status: {response.status_code}")
    if response.status_code in [200, 204]:
        print("✅ PUT works instead of PATCH!")
    else:
        print(f"❌ PUT also failed: {response.text[:150] if response.text else 'No message'}")
except Exception as e:
    print(f"💥 PUT Exception: {str(e)}")

print("\nConclusion: Check which endpoint format (if any) returned a 200/204 status code")
