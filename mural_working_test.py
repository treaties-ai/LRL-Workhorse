#!/usr/bin/env python3
"""
MURAL Working Test - Using insights from debugging report and sanitization guide
This implementation uses the correct payload structure and balanced text sanitization
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
WORKSPACE_ID = "root7380"
BOARD_ID = "1754493659737"

def sanitize_for_mural_display(text):
    """
    Balanced sanitization - preserves readability while ensuring API compatibility
    Based on mural-sanitization-guide.md
    """
    if not text or not isinstance(text, str):
        return ''
    
    # Layer 1: Remove only DANGEROUS Unicode, keep formatting
    # Remove control chars EXCEPT newlines, carriage returns, and tabs
    import re
    text = re.sub(r'[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F]', '', text)
    
    # Remove zero-width and directional characters (security threats)
    text = re.sub(r'[\u200B-\u200F]', '', text)
    text = re.sub(r'[\u202A-\u202E]', '', text)
    text = re.sub(r'[\u2060-\u206F]', '', text)
    text = re.sub(r'[\uFEFF]', '', text)
    
    # Remove surrogate pairs (can cause JSON parsing errors)
    text = re.sub(r'[\uD800-\uDFFF]', '', text)
    
    # Remove specials block
    text = re.sub(r'[\uFFF0-\uFFFF]', '', text)
    
    # Layer 2: Remove specific API-breaking characters (learned from testing)
    # Box-drawing characters that break Mural API
    text = re.sub(r'[━─│┌┐└┘┬┤┴├┼]', '', text)
    
    # Remove bullet character
    text = text.replace('•', '-')
    
    # Layer 3: Normalize problematic punctuation (keep functionality)
    text = re.sub(r"[''‚‛]", "'", text)
    text = re.sub(r'[""„‟]', '"', text)
    text = re.sub(r'[–—]', '-', text)
    text = re.sub(r'[…]', '...', text)
    
    # Layer 4: Safe character replacements (preserve meaning)
    text = text.replace('<', '').replace('>', '')  # Remove angle brackets
    text = text.replace('$', 'S')  # Replace $ with S for safety
    text = text.replace('\\', '/')  # Replace backslash
    text = text.replace('`', "'")  # Replace backtick
    
    # Layer 5: Preserve line structure while cleaning excess whitespace
    # Replace multiple spaces with single space (but not newlines!)
    text = re.sub(r' +', ' ', text)
    
    # Trim each line but keep the line breaks
    lines = text.split('\n')
    text = '\n'.join(line.strip() for line in lines)
    
    # Layer 6: Smart length limiting with formatting preservation
    MAX_LENGTH = 300
    if len(text) > MAX_LENGTH:
        # Try to cut at a newline for cleaner truncation
        cut_point = text.rfind('\n', 0, MAX_LENGTH)
        if cut_point > MAX_LENGTH - 50 and cut_point > 0:
            text = text[:cut_point] + '\n...'
        else:
            text = text[:MAX_LENGTH] + '...'
    
    return text

print("\n" + "="*70)
print("MURAL WORKING TEST - CREATING STICKY NOTES WITH BALANCED SANITIZATION")
print("="*70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Board URL: https://app.mural.co/t/{WORKSPACE_ID}/m/{WORKSPACE_ID}/{BOARD_ID}")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Test 1: Create a single sticky note with simple text
print("\n" + "-"*60)
print("TEST 1: Single sticky note with simple text")
print("-"*60)

# The correct endpoint - need to use combined workspace.board format
# From API explorer, this format worked: /murals/root7380.1754493659737
combined_id = f"{WORKSPACE_ID}.{BOARD_ID}"
endpoint = f"https://app.mural.co/api/public/v1/murals/{combined_id}/widgets/sticky-note"

print(f"Using endpoint: {endpoint}")

# Correct payload structure from debugging report
simple_payload = {
    "shape": "rectangle",  # REQUIRED
    "text": "Test Sticky Note - Simple",
    "x": 100,
    "y": 100,
    "width": 138,  # Standard size
    "height": 138
    # NO style field during creation!
}

print(f"Payload: {json.dumps(simple_payload, indent=2)}")

try:
    response = requests.post(endpoint, headers=headers, json=simple_payload, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print("✅ SUCCESS! Created simple sticky note")
        print(f"Response: {response.text[:200]}")
    else:
        print(f"❌ Failed: {response.text[:300]}")
except Exception as e:
    print(f"💥 Error: {str(e)}")

# Test 2: Create a sticky note with formatted text that needs sanitization
print("\n" + "-"*60)
print("TEST 2: Sticky note with text that needs balanced sanitization")
print("-"*60)

# Text with problematic characters
problematic_text = """THREAT DETECTION
━━━━━━━━━━━━━━━━━━━━━

• AI-Powered Threat System
• €15,000,000 value

RISK SCORE: 8/10"""

sanitized_text = sanitize_for_mural_display(problematic_text)

print("Original text:")
print(problematic_text)
print("\nSanitized text:")
print(sanitized_text)

formatted_payload = {
    "shape": "rectangle",
    "text": sanitized_text,
    "x": 300,
    "y": 100,
    "width": 138,
    "height": 138
}

try:
    response = requests.post(endpoint, headers=headers, json=formatted_payload, timeout=10)
    print(f"\nStatus: {response.status_code}")
    if response.status_code in [200, 201]:
        print("✅ SUCCESS! Created sticky note with sanitized text")
    else:
        print(f"❌ Failed: {response.text[:300]}")
except Exception as e:
    print(f"💥 Error: {str(e)}")

# Test 3: Create multiple sticky notes in a batch
print("\n" + "-"*60)
print("TEST 3: Creating multiple sticky notes")
print("-"*60)

sticky_notes = [
    {
        "shape": "rectangle",
        "text": "Body Visualization",
        "x": 100,
        "y": 300,
        "width": 138,
        "height": 138
    },
    {
        "shape": "rectangle",
        "text": "HEAD",
        "x": 400,
        "y": 300,
        "width": 138,
        "height": 138
    },
    {
        "shape": "rectangle",
        "text": "HEART",
        "x": 400,
        "y": 450,
        "width": 138,
        "height": 138
    },
    {
        "shape": "rectangle",
        "text": "TORSO",
        "x": 400,
        "y": 600,
        "width": 138,
        "height": 138
    },
    {
        "shape": "rectangle",
        "text": "LEFT ARM",
        "x": 250,
        "y": 500,
        "width": 138,
        "height": 138
    },
    {
        "shape": "rectangle",
        "text": "RIGHT ARM",
        "x": 550,
        "y": 500,
        "width": 138,
        "height": 138
    }
]

created_count = 0
for idx, sticky in enumerate(sticky_notes, 1):
    try:
        print(f"Creating sticky {idx}/{len(sticky_notes)}: {sticky['text']}")
        response = requests.post(endpoint, headers=headers, json=sticky, timeout=10)
        if response.status_code in [200, 201]:
            print(f"  ✅ Created: {sticky['text']}")
            created_count += 1
        else:
            print(f"  ❌ Failed: {response.status_code}")
        
        # Small delay between requests to avoid rate limiting
        time.sleep(0.5)
    except Exception as e:
        print(f"  💥 Error: {str(e)}")

print(f"\nCreated {created_count}/{len(sticky_notes)} sticky notes")

# Test 4: Complex text with proper sanitization
print("\n" + "-"*60)
print("TEST 4: Complex text showing balanced sanitization")
print("-"*60)

complex_texts = [
    {
        "original": "COMPANIES AT RISK\n━━━━━━━━━━━━━━━━━━━\n\n• TechDefense GmbH\n• AISecure Systems Ltd\n\nHigh-risk contractors",
        "x": 700,
        "y": 300
    },
    {
        "original": "Deep grief in chest\nTDAI: 8.5\n\nGrounded feeling\nTDAI: 7.5",
        "x": 700,
        "y": 500
    }
]

for idx, item in enumerate(complex_texts, 1):
    original = item["original"]
    sanitized = sanitize_for_mural_display(original)
    
    print(f"\nText {idx}:")
    print(f"Original ({len(original)} chars):")
    print(original)
    print(f"\nSanitized ({len(sanitized)} chars):")
    print(sanitized)
    
    payload = {
        "shape": "rectangle",
        "text": sanitized,
        "x": item["x"],
        "y": item["y"],
        "width": 200,  # Larger for more text
        "height": 150
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            print("✅ Successfully created sticky note with complex text")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"💥 Error: {str(e)}")
    
    time.sleep(0.5)

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

print("\nKey Findings from Documentation:")
print("1. ✅ Use 'shape': 'rectangle' (REQUIRED)")
print("2. ✅ NO style field during creation")
print("3. ✅ Standard dimensions: 138x138")
print("4. ✅ Balanced sanitization preserves readability")
print("5. ✅ Remove only problematic Unicode (box-drawing, zero-width)")

print(f"\n🎯 Check your Mural board at:")
print(f"   https://app.mural.co/t/{WORKSPACE_ID}/m/{WORKSPACE_ID}/{BOARD_ID}")
print("\nThe board should now show:")
print("  • Simple sticky notes")
print("  • Properly sanitized formatted text")
print("  • Body visualization elements")
print("  • Complex text with preserved formatting")
