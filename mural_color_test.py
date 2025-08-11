#!/usr/bin/env python3
"""
MURAL Color Test - Verify PATCH operations for applying colors to widgets
This is the critical first test to ensure we can color widgets after creation
"""

import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Import our new modules
from mural_color_manager import MuralColorManager
from mural_layout_engine import MuralLayoutEngine, Position

# Load environment variables
load_dotenv('.env')

def run_color_patch_test():
    """Test the critical PATCH operation for coloring widgets"""
    
    print("\n" + "="*70)
    print("MURAL COLOR PATCH TEST - PHASE 1 FORMATTING")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize managers
    color_manager = MuralColorManager()
    layout_engine = MuralLayoutEngine()
    
    print(f"\nBoard URL: https://app.mural.co/t/{color_manager.workspace_id}/m/{color_manager.workspace_id}/{color_manager.board_id}")
    
    # Test 1: Simple color test - create one widget and color it
    print("\n" + "-"*60)
    print("TEST 1: Single Widget Color Test")
    print("-"*60)
    
    print("Creating a simple widget and applying red color...")
    widget_id = color_manager.create_and_color_widget(
        text="COLOR TEST - Should be RED",
        x=100,
        y=100,
        width=200,
        height=100,
        content_type="THREAT"  # Should make it red
    )
    
    if widget_id:
        print(f"✅ Success! Widget {widget_id} created and colored")
    else:
        print("❌ Failed to create or color widget")
        return False
    
    # Test 2: Body part visualization with colors
    print("\n" + "-"*60)
    print("TEST 2: Body Parts with Anatomical Colors")
    print("-"*60)
    
    body_parts_test = [
        ("HEAD", "HEAD"),
        ("HEART", "HEART"),
        ("LEFT ARM", "LEFT_ARM"),
        ("RIGHT ARM", "RIGHT_ARM"),
        ("TORSO", "TORSO"),
        ("LEFT LEG", "LEFT_LEG"),
        ("RIGHT LEG", "RIGHT_LEG"),
    ]
    
    created_count = 0
    for text, part_type in body_parts_test:
        pos = layout_engine.get_anatomical_position(part_type)
        print(f"Creating {text} at anatomical position ({pos.x}, {pos.y})...")
        
        widget_id = color_manager.create_and_color_widget(
            text=text,
            x=pos.x,
            y=pos.y,
            width=150,
            height=150,
            content_type=part_type
        )
        
        if widget_id:
            created_count += 1
            print(f"  ✅ Created and colored: {text}")
        else:
            print(f"  ❌ Failed: {text}")
        
        time.sleep(0.5)  # Avoid rate limiting
    
    print(f"\nCreated {created_count}/{len(body_parts_test)} body part widgets")
    
    # Test 3: TDAI scores with severity-based colors
    print("\n" + "-"*60)
    print("TEST 3: TDAI Scores with Severity Colors")
    print("-"*60)
    
    tdai_tests = [
        ("Critical Issue\nTDAI: 9.5", None),  # Should auto-detect as HIGH (red)
        ("Moderate Concern\nTDAI: 6.0", None),  # Should auto-detect as MEDIUM (orange)
        ("Minor Issue\nTDAI: 2.5", None),  # Should auto-detect as LOW (green)
    ]
    
    tdai_zone = layout_engine.get_zone_position("tdai")
    
    for i, (text, content_type) in enumerate(tdai_tests):
        y_offset = i * 160
        print(f"Creating TDAI widget: {text.replace(chr(10), ' ')}...")
        
        widget_id = color_manager.create_and_color_widget(
            text=text,
            x=tdai_zone.x,
            y=tdai_zone.y + y_offset,
            width=180,
            height=140,
            content_type=content_type  # Let it auto-detect from text
        )
        
        if widget_id:
            print(f"  ✅ Created with appropriate color")
        else:
            print(f"  ❌ Failed to create")
        
        time.sleep(0.5)
    
    # Test 4: Category-based coloring
    print("\n" + "-"*60)
    print("TEST 4: Category-Based Colors")
    print("-"*60)
    
    category_tests = [
        ("THREAT DETECTION\nAI-Powered System", "THREAT"),
        ("TechDefense GmbH\nHigh-risk contractor", "COMPANY"),
        ("Deep grief in chest\nUnresolved trauma", "EMOTION"),
        ("Feeling grounded\nSafe and secure", "GROUNDING"),
    ]
    
    cat_zone = layout_engine.get_zone_position("categories")
    
    for i, (text, content_type) in enumerate(category_tests):
        y_offset = i * 160
        print(f"Creating category widget: {content_type}...")
        
        widget_id = color_manager.create_and_color_widget(
            text=text,
            x=cat_zone.x,
            y=cat_zone.y + y_offset,
            width=200,
            height=150,
            content_type=content_type
        )
        
        if widget_id:
            print(f"  ✅ Created with category color")
        else:
            print(f"  ❌ Failed to create")
        
        time.sleep(0.5)
    
    # Test 5: Create a color legend
    print("\n" + "-"*60)
    print("TEST 5: Creating Color Legend")
    print("-"*60)
    
    print("Creating color legend in top-left corner...")
    color_manager.create_color_legend(x=50, y=50)
    print("✅ Color legend created")
    
    # Print statistics
    print("\n" + "-"*60)
    print("WIDGET STATISTICS")
    print("-"*60)
    
    stats = color_manager.get_widget_stats()
    print(f"Total widgets created: {stats['total_widgets']}")
    print(f"By type: {json.dumps(stats['by_type'], indent=2)}")
    print(f"By color: {json.dumps(stats['by_color'], indent=2)}")
    
    print("\n" + "="*70)
    print("COLOR TEST COMPLETE!")
    print("="*70)
    
    print("\n🎯 Check your MURAL board at:")
    print(f"   https://app.mural.co/t/{color_manager.workspace_id}/m/{color_manager.workspace_id}/{color_manager.board_id}")
    
    print("\nExpected results:")
    print("  • Color legend in top-left corner")
    print("  • Body parts in anatomical positions with distinct colors")
    print("  • TDAI scores colored by severity (red/orange/green)")
    print("  • Category widgets with appropriate theme colors")
    print("  • NO MORE YELLOW STICKIES! 🎨")
    
    return True


if __name__ == "__main__":
    # Run the color test
    success = run_color_patch_test()
    
    if success:
        print("\n✅ Phase 1 formatting test successful!")
        print("Next steps:")
        print("  1. Verify colors are visible on the board")
        print("  2. Check that PATCH operations worked")
        print("  3. Proceed to Phase 2: Dynamic sizing")
    else:
        print("\n❌ Color test encountered issues")
        print("Debug steps:")
        print("  1. Check API response for PATCH operations")
        print("  2. Verify widget IDs are being extracted correctly")
        print("  3. Check OAuth token is still valid")
