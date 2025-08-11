#!/usr/bin/env python3
"""
MURAL Shape Test - Based on error message showing the API expects shapes
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
print("MURAL SHAPE & WIDGET API - COMPREHENSIVE TESTING")
print("="*70)
print(f"Testing based on error: API expects 'shape' property with 'circle', 'rectangle'")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Test 1: Try creating a shape as the error suggested
print("\n" + "-"*60)
print("TEST 1: Creating shapes (as error message indicated)")
print("-"*60)

shape_endpoint = f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/sticky-note"

shape_payloads = [
    # Test with circle
    {
        "shape": "circle",
        "x": 100,
        "y": 100,
        "width": 100,
        "height": 100,
        "style": {
            "backgroundColor": "#FF6B6B"
        }
    },
    
    # Test with rectangle
    {
        "shape": "rectangle",
        "x": 250,
        "y": 100,
        "width": 150,
        "height": 100,
        "style": {
            "backgroundColor": "#4ECDC4"
        }
    },
    
    # Rectangle with text
    {
        "shape": "rectangle",
        "text": "Test Rectangle with Text",
        "x": 450,
        "y": 100,
        "width": 200,
        "height": 100,
        "style": {
            "backgroundColor": "#FFD93D"
        }
    }
]

for idx, payload in enumerate(shape_payloads, 1):
    print(f"\n[Shape {idx}] {payload.get('shape', 'unknown')} at ({payload.get('x')}, {payload.get('y')})")
    try:
        response = requests.post(shape_endpoint, headers=headers, json=payload, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"  ✅ SUCCESS! Created {payload['shape']}")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            
            # Save successful configuration
            with open('mural_working_shape.json', 'w') as f:
                json.dump({
                    "endpoint": shape_endpoint,
                    "payload": payload,
                    "response": response.json(),
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
        else:
            print(f"  Error: {response.text[:150]}")
    except Exception as e:
        print(f"  Exception: {str(e)}")

# Test 2: Try different endpoints for sticky notes
print("\n" + "-"*60)
print("TEST 2: Finding the actual sticky note endpoint")
print("-"*60)

# Different endpoint patterns to test
sticky_note_endpoints = [
    # Remove the /sticky-note suffix (just widgets)
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets",
    f"https://app.mural.co/api/public/v1/murals/root7380.{BOARD_ID}/widgets",
    
    # Try with 'shape' = 'sticky-note'
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets",
    
    # Try text endpoint
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/text",
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/text",
    
    # Try note endpoint
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/widgets/note",
    f"https://app.mural.co/api/public/v1/murals/{BOARD_ID}/notes",
]

# Different payload formats for sticky notes
sticky_payloads = [
    # Format 1: shape = sticky-note
    {
        "shape": "sticky-note",
        "text": "Test Sticky 1",
        "x": 100,
        "y": 300,
        "style": {
            "backgroundColor": "#FFFF00"
        }
    },
    
    # Format 2: type = sticky-note
    {
        "type": "sticky-note",
        "text": "Test Sticky 2",
        "x": 300,
        "y": 300,
        "style": {
            "backgroundColor": "#FFD93D"
        }
    },
    
    # Format 3: shape = note
    {
        "shape": "note",
        "text": "Test Sticky 3",
        "x": 500,
        "y": 300,
        "style": {
            "backgroundColor": "#6BCF7F"
        }
    },
    
    # Format 4: widget type
    {
        "widgetType": "sticky-note",
        "text": "Test Sticky 4",
        "x": 100,
        "y": 500
    },
    
    # Format 5: Just text (for text endpoints)
    {
        "text": "Test Text Widget",
        "x": 300,
        "y": 500,
        "style": {
            "fontSize": 14,
            "color": "#000000"
        }
    }
]

success_found = False

for endpoint in sticky_note_endpoints:
    if success_found:
        break
        
    print(f"\nTesting endpoint: {endpoint}")
    
    for payload_idx, payload in enumerate(sticky_payloads, 1):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"  ✅ SUCCESS with payload format {payload_idx}!")
                print(f"     Keys: {list(payload.keys())}")
                print(f"     Response: {response.text[:200]}")
                
                # Save working configuration
                with open('mural_working_sticky.json', 'w') as f:
                    json.dump({
                        "endpoint": endpoint,
                        "payload_format": payload_idx,
                        "payload": payload,
                        "response": response.json(),
                        "timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                
                success_found = True
                break
                
            elif response.status_code == 404 and payload_idx == 1:
                print(f"  404 - Endpoint not found")
                break  # No point trying other payloads
                
            elif response.status_code == 400:
                # Parse error to understand what's expected
                try:
                    error_data = response.json()
                    if 'details' in error_data and error_data['details']:
                        first_error = error_data['details'][0].get('message', '')
                        if 'Invalid' in first_error and payload_idx == 1:
                            print(f"  400 - {first_error[:100]}")
                except:
                    pass
                    
        except Exception as e:
            if payload_idx == 1:
                print(f"  Error: {str(e)[:100]}")

# Test 3: Try the combined endpoint with workspace ID
print("\n" + "-"*60)
print("TEST 3: Testing with workspace.board ID format")
print("-"*60)

combined_id = f"{WORKSPACE_ID}.{BOARD_ID}"
combined_endpoints = [
    f"https://app.mural.co/api/public/v1/murals/{combined_id}/widgets",
    f"https://app.mural.co/api/public/v1/boards/{combined_id}/widgets",
]

test_payload = {
    "shape": "rectangle",  # Use what we know works
    "text": "Testing Combined ID",
    "x": 700,
    "y": 300,
    "width": 200,
    "height": 100,
    "style": {
        "backgroundColor": "#E74C3C"
    }
}

for endpoint in combined_endpoints:
    print(f"\nTesting: {endpoint}")
    try:
        response = requests.post(endpoint, headers=headers, json=test_payload, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"  ✅ SUCCESS with combined ID!")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  Error: {str(e)}")

# Summary
print("\n" + "="*70)
print("DISCOVERY SUMMARY")
print("="*70)

print("\nKey Findings:")
print("1. The /widgets/sticky-note endpoint expects 'shape' property with 'circle' or 'rectangle'")
print("2. This suggests sticky notes might be created differently in the v1 API")
print("3. Shapes (circle, rectangle) can likely be created with text")
print("4. The actual sticky note creation method remains unclear")

print("\nRecommendations:")
print("1. Use rectangles with text as a workaround for sticky notes")
print("2. Check MURAL's latest API documentation for v1 sticky note creation")
print("3. Consider using the v0 API if available with proper authentication")
print("4. Contact MURAL support for clarification on sticky note creation in v1 API")

# Check if any files were created
import os
if os.path.exists('mural_working_shape.json'):
    print("\n✅ Successfully created shapes! Check mural_working_shape.json")
if os.path.exists('mural_working_sticky.json'):
    print("✅ Successfully created sticky notes! Check mural_working_sticky.json")
