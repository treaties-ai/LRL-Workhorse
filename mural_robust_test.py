#!/usr/bin/env python3
"""
Robust Mural API Test using the existing implementation
Creates real sticky notes with body visualization
"""

import sys
import os
import time
import logging
from typing import Dict, List

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our existing implementation
from mural_core_api import MuralCoreAPI, APIResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MuralRobustTest')

def test_mural_api():
    """Test the Mural API with real credentials"""
    
    print("\n" + "="*60)
    print("MURAL API ROBUST TEST - REAL STICKY NOTES")
    print("="*60)
    
    # Initialize the API with robust auto-healing
    logger.info("Initializing Mural API with auto-healing...")
    # We're already in lrl-workhorse directory
    api = MuralCoreAPI("mural_config.json")
    
    # Use the existing board from config
    board_id = "1754493659737"
    workspace_id = "root7380"
    mural_id = f"{workspace_id}.{board_id}"
    
    logger.info(f"Using board: {mural_id}")
    board_url = f"https://app.mural.co/t/{workspace_id}/m/{workspace_id}/{board_id}"
    print(f"\n🌐 Board URL: {board_url}")
    
    # Test 1: Create body visualization sticky notes
    print("\n--- Creating Body Visualization ---")
    body_parts = [
        {"name": "HEAD", "x": 400, "y": 100, "color": "#E0E0E0"},
        {"name": "HEART ♥", "x": 390, "y": 250, "color": "#FF6B6B"},
        {"name": "TORSO", "x": 400, "y": 350, "color": "#E0E0E0"},
        {"name": "L-ARM", "x": 250, "y": 300, "color": "#E0E0E0"},
        {"name": "R-ARM", "x": 550, "y": 300, "color": "#E0E0E0"},
        {"name": "L-LEG", "x": 350, "y": 500, "color": "#E0E0E0"},
        {"name": "R-LEG", "x": 450, "y": 500, "color": "#E0E0E0"}
    ]
    
    created_count = 0
    for part in body_parts:
        logger.info(f"Creating {part['name']}...")
        result = api.create_sticky_note(
            mural_id=mural_id,
            text=part["name"],
            x=part["x"],
            y=part["y"],
            color=part["color"]
        )
        
        if result.success:
            created_count += 1
            print(f"  ✓ Created {part['name']}")
        else:
            print(f"  ✗ Failed to create {part['name']}: {result.error}")
        
        time.sleep(0.5)  # Small delay between API calls
    
    print(f"\nBody visualization: {created_count}/{len(body_parts)} parts created")
    
    # Test 2: Create somatic mapping notes with TDAI scores
    print("\n--- Creating Somatic Mapping Notes ---")
    somatic_notes = [
        {
            "text": "Deep grief in chest - TDAI 8.5",
            "x": 390,
            "y": 280,
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
            "y": 530,
            "color": "#2ECC71"  # Deep green
        },
        {
            "text": "Creative flow - TDAI 7.0",
            "x": 550,
            "y": 330,
            "color": "#2ECC71"  # Deep green
        },
        {
            "text": "Surface tension - TDAI 3.5",
            "x": 250,
            "y": 330,
            "color": "#FFD93D"  # Yellow for medium TDAI
        }
    ]
    
    somatic_count = 0
    for note in somatic_notes:
        logger.info(f"Creating somatic note: {note['text'][:20]}...")
        result = api.create_sticky_note(
            mural_id=mural_id,
            text=note["text"],
            x=note["x"],
            y=note["y"],
            color=note["color"]
        )
        
        if result.success:
            somatic_count += 1
            print(f"  ✓ Created: {note['text'][:30]}")
        else:
            print(f"  ✗ Failed: {note['text'][:30]} - {result.error}")
        
        time.sleep(0.5)
    
    print(f"\nSomatic mapping: {somatic_count}/{len(somatic_notes)} notes created")
    
    # Test 3: Test batch operations (smaller batch for safety)
    print("\n--- Testing Batch Operations ---")
    batch_notes = [
        {"text": f"Batch test {i+1}", "x": 700 + (i * 50), "y": 200}
        for i in range(3)
    ]
    
    batch_count = 0
    for note in batch_notes:
        result = api.create_sticky_note(
            mural_id=mural_id,
            text=note["text"],
            x=note["x"],
            y=note["y"],
            color="#FFD93D"
        )
        
        if result.success:
            batch_count += 1
            print(f"  ✓ {note['text']}")
        else:
            print(f"  ✗ {note['text']}: {result.error}")
        
        time.sleep(0.3)
    
    print(f"\nBatch test: {batch_count}/{len(batch_notes)} created")
    
    # Health check
    print("\n--- System Health Check ---")
    health = api.health_check()
    for key, value in health.items():
        emoji = "✓" if value == "healthy" else "⚠️" if value == "warning" else "✗"
        print(f"  {emoji} {key}: {value}")
    
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
    print("  • Somatic mapping notes with TDAI color coding")
    print("  • Test batch notes")
    print("="*60)
    
    return total_created > 0

if __name__ == "__main__":
    try:
        success = test_mural_api()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed - check logs for details")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
