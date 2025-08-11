#!/usr/bin/env python3
"""
Direct Mural API Test - Uses existing access token to create sticky notes
"""

import os
import json
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Get credentials from .env
ACCESS_TOKEN = os.getenv('MURAL_ACCESS_TOKEN')
WORKSPACE_ID = "root7380"
BOARD_ID = "1754493659737"
MURAL_ID = f"{WORKSPACE_ID}.{BOARD_ID}"  # Combined format

print("\n" + "="*60)
print("MURAL DIRECT API TEST - CREATING STICKY NOTES")
print("="*60)

if not ACCESS_TOKEN:
    print("❌ No access token found in .env file")
    exit(1)

print(f"✓ Access token loaded: {ACCESS_TOKEN[:30]}...")
print(f"✓ Workspace: {WORKSPACE_ID}")
print(f"✓ Board ID: {BOARD_ID}")
print(f"✓ Mural ID: {MURAL_ID}")

# Board URL for reference
board_url = f"https://app.mural.co/t/{WORKSPACE_ID}/m/{WORKSPACE_ID}/{BOARD_ID}"
print(f"\n🌐 Board URL: {board_url}")
print("Make sure this board is open in your browser!")

# Set up headers
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# API endpoint for creating widgets - using v0 API with workspace.board format
api_url = f"https://api.mural.co/api/v0/murals/{MURAL_ID}/widgets"

def create_sticky_note(text, x, y, color="#FFFF00", width=200, height=200):
    """Create a sticky note on the Mural board"""
    
    widget_data = {
        "type": "sticky-note",
        "text": text,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "style": {
            "backgroundColor": color,
            "fontSize": 14,
            "textAlign": "center"
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=widget_data, timeout=10)
        
        if response.status_code in [200, 201]:
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
print("Creating sticky notes arranged in body shape...")

# Body parts with coordinates (arranged in body shape)
body_parts = [
    {"text": "HEAD", "x": 400, "y": 100, "color": "#E0E0E0"},
    {"text": "HEART ♥", "x": 390, "y": 250, "color": "#FF6B6B"},
    {"text": "TORSO", "x": 400, "y": 350, "color": "#E0E0E0"},
    {"text": "L-ARM", "x": 250, "y": 300, "color": "#E0E0E0"},
    {"text": "R-ARM", "x": 550, "y": 300, "color": "#E0E0E0"},
    {"text": "L-LEG", "x": 350, "y": 500, "color": "#E0E0E0"},
    {"text": "R-LEG", "x": 450, "y": 500, "color": "#E0E0E0"}
]

created_count = 0
for part in body_parts:
    if create_sticky_note(part["text"], part["x"], part["y"], part["color"]):
        created_count += 1
    time.sleep(0.5)  # Small delay between API calls

print(f"\nBody visualization: {created_count}/{len(body_parts)} parts created")

print("\n--- Creating Somatic Mapping Notes ---")
print("Adding notes with TDAI (Therapist Depth Assessment Index) scores...")

# Somatic notes with TDAI scoring
# TDAI Color mapping:
# - Red (#E74C3C): Shallow (1-3)
# - Yellow (#FFD93D): Medium (3-5)
# - Light Green (#6BCF7F): Deep (5-7)
# - Deep Green (#2ECC71): Very Deep (7-10)

somatic_notes = [
    {
        "text": "Deep grief in chest\nTDAI: 8.5",
        "x": 390,
        "y": 280,
        "color": "#2ECC71"  # Deep green for high TDAI
    },
    {
        "text": "Racing thoughts\nTDAI: 6.0",
        "x": 400,
        "y": 130,
        "color": "#6BCF7F"  # Light green
    },
    {
        "text": "Grounded feeling\nTDAI: 7.5",
        "x": 350,
        "y": 530,
        "color": "#2ECC71"  # Deep green
    },
    {
        "text": "Creative flow\nTDAI: 7.0",
        "x": 550,
        "y": 330,
        "color": "#2ECC71"  # Deep green
    },
    {
        "text": "Surface tension\nTDAI: 3.5",
        "x": 250,
        "y": 330,
        "color": "#FFD93D"  # Yellow for medium TDAI
    },
    {
        "text": "Shallow breathing\nTDAI: 2.0",
        "x": 400,
        "y": 200,
        "color": "#E74C3C"  # Red for shallow TDAI
    }
]

somatic_count = 0
for note in somatic_notes:
    if create_sticky_note(note["text"], note["x"], note["y"], note["color"]):
        somatic_count += 1
    time.sleep(0.5)

print(f"\nSomatic mapping: {somatic_count}/{len(somatic_notes)} notes created")

# Test batch creation with smaller sizes
print("\n--- Testing Batch Creation ---")
batch_notes = [
    {"text": f"Agent Output {i+1}", "x": 700 + (i * 60), "y": 200}
    for i in range(5)
]

batch_count = 0
for note in batch_notes:
    if create_sticky_note(note["text"], note["x"], note["y"], "#FFD93D"):
        batch_count += 1
    time.sleep(0.3)

print(f"\nBatch test: {batch_count}/{len(batch_notes)} created")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
total_created = created_count + somatic_count + batch_count
total_attempted = len(body_parts) + len(somatic_notes) + len(batch_notes)
success_rate = (total_created / total_attempted * 100) if total_attempted > 0 else 0

print(f"Total sticky notes created: {total_created}/{total_attempted}")
print(f"Success rate: {success_rate:.1f}%")
print(f"\n🎯 Check your Mural board at:")
print(f"   {board_url}")
print("\nThe board should now show:")
print("  • Body visualization (head, torso, arms, legs)")
print("  • Somatic mapping notes with TDAI color coding:")
print("    - 🔴 Red: Shallow (TDAI 1-3)")
print("    - 🟡 Yellow: Medium (TDAI 3-5)")
print("    - 🟢 Light Green: Deep (TDAI 5-7)")
print("    - 🟢 Deep Green: Very Deep (TDAI 7-10)")
print("  • Test batch notes for agent outputs")
print("="*60)

if total_created > 0:
    print("\n✅ Test completed successfully!")
    print("   Your board has been populated with sticky notes!")
else:
    print("\n❌ Test failed - check the access token and try again")
