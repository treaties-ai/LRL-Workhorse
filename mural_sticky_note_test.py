#!/usr/bin/env python3
"""
MURAL Sticky Note Endpoint Test - Testing the specific endpoint that returned 400 (not 404)
"""

import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('.env')

ACCESS_TOKEN = os.getenv('MURAL_ACCESS_TOKEN')
WORKSPACE_ID = "root7380"
BOARD_ID = "1754493659737"

print("\n" + "="*70)
print("MURAL STICKY NOTE ENDPOINT - TARGETED TESTING")
print("="*70)
print(f"Testing endpoint that returned 400 (exists but wrong format)")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# The endpoint that returned 400 (meaning it exists!)
endpoint = f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/sticky-note"

# Different payload formats to test based on the error message
test_payloads = [
    # Format 1: Without type field (since endpoint already specifies sticky-note)
    {
        "text": "Test Sticky Note 1",
        "x": 100,
        "y": 100,
        "style": {
            "backgroundColor": "#FFFF00"
        }
    },
    
    # Format 2: With content wrapper
    {
        "content": {
            "text": "Test Sticky Note 2"
        },
        "x": 100,
        "y": 200,
        "style": {
            "backgroundColor": "#FFD93D"
        }
    },
    
    # Format 3: Minimal - just text and position
    {
        "text": "Test Sticky Note 3",
        "x": 100,
        "y": 300
    },
    
    # Format 4: With 'data' wrapper
    {
        "data": {
            "text": "Test Sticky Note 4"
        },
        "x": 100,
        "y": 400
    },
    
    # Format 5: Following MURAL's potential schema
    {
        "text": "Test Sticky Note 5",
        "position": {
            "x": 100,
            "y": 500
        },
        "style": {
            "backgroundColor": "#6BCF7F"
        }
    },
    
    # Format 6: With dimensions
    {
        "text": "Test Sticky Note 6",
        "x": 100,
        "y": 600,
        "width": 200,
        "height": 200,
        "style": {
            "backgroundColor": "#E74C3C"
        }
    },
    
    # Format 7: Following potential v1 API structure
    {
        "properties": {
            "text": "Test Sticky Note 7"
        },
        "geometry": {
            "x": 100,
            "y": 700,
            "width": 200,
            "height": 200
        }
    },
    
    # Format 8: Simple with title instead of text
    {
        "title": "Test Sticky Note 8",
        "x": 100,
        "y": 800
    },
    
    # Format 9: With content as string
    {
        "content": "Test Sticky Note 9",
        "x": 100,
        "y": 900
    },
    
    # Format 10: Nested under widget
    {
        "widget": {
            "text": "Test Sticky Note 10",
            "x": 100,
            "y": 1000
        }
    }
]

print(f"\nTesting {len(test_payloads)} different payload formats...")
print("="*70)

successful_format = None

for idx, payload in enumerate(test_payloads, 1):
    print(f"\n[Format {idx}] Testing payload structure:")
    # Show abbreviated payload structure
    print(f"  Keys: {list(payload.keys())}")
    
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"  ✅ SUCCESS! Found working format!")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            successful_format = idx
            
            # Save successful format
            with open('mural_working_format.json', 'w') as f:
                json.dump({
                    "endpoint": endpoint,
                    "working_format": idx,
                    "payload": payload,
                    "response": response.json(),
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            
            break
        else:
            response_text = response.text[:200]
            if "Invalid" in response_text or "error" in response_text.lower():
                print(f"  Error details: {response_text}")
            
    except Exception as e:
        print(f"  💥 Exception: {str(e)}")

# Try alternative endpoints with successful format
if successful_format:
    print("\n" + "="*70)
    print("TESTING OTHER ENDPOINTS WITH SUCCESSFUL FORMAT")
    print("="*70)
    
    working_payload = test_payloads[successful_format - 1]
    
    alternative_endpoints = [
        f"https://app.mural.co/api/public/v1/murals/root7380.{BOARD_ID}/widgets/sticky-note",
        f"https://app.mural.co/api/public/v1/boards/{BOARD_ID}/widgets/sticky-note",
        f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets",
    ]
    
    for alt_endpoint in alternative_endpoints:
        print(f"\nTesting: {alt_endpoint}")
        try:
            response = requests.post(
                alt_endpoint,
                headers=headers,
                json=working_payload,
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"  ✅ This endpoint also works!")
        except Exception as e:
            print(f"  Error: {str(e)}")

# Summary
print("\n" + "="*70)
print("TESTING SUMMARY")
print("="*70)

if successful_format:
    print(f"✅ SUCCESS! Found working format: #{successful_format}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Working payload saved to: mural_working_format.json")
    print("\nNext steps:")
    print("1. Update all test files with the working format")
    print("2. Test batch creation with this format")
    print("3. Create your visualization on the board!")
else:
    print("❌ No working format found")
    print("\nPossible next steps:")
    print("1. The API might require additional headers (API version, etc.)")
    print("2. The endpoint might need URL parameters")
    print("3. Check if the board requires special permissions")
    print("4. The API documentation may be outdated - contact MURAL support")
    
    # Show the most informative error
    print("\nMost informative error was from Format 1:")
    print("'Invalid \"shape\" property' - This suggests the API expects different fields")
