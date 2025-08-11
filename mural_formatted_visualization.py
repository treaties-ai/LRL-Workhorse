#!/usr/bin/env python3
"""
MURAL Formatted Visualization - Working within API limitations
Focus on positioning, sizing, and text formatting since colors are not supported
"""

import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from mural_working_test import sanitize_for_mural_display
from mural_layout_engine import MuralLayoutEngine, Position

# Load environment variables
load_dotenv('.env')

class MuralFormattedVisualization:
    """Create a formatted MURAL visualization using positioning and sizing"""
    
    def __init__(self):
        self.access_token = os.getenv('MURAL_ACCESS_TOKEN')
        self.board_id = os.getenv('MURAL_BOARD_ID', 'root7380.1754493659737')
        self.base_url = "https://app.mural.co/api/public/v1"
        self.layout_engine = MuralLayoutEngine()
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        self.created_widgets = []
    
    def create_widget(self, text, x, y, width=138, height=138):
        """Create a sticky note widget"""
        endpoint = f"{self.base_url}/murals/{self.board_id}/widgets/sticky-note"
        
        sanitized_text = sanitize_for_mural_display(text)
        
        payload = {
            "shape": "rectangle",
            "text": sanitized_text,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        try:
            import requests
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                widget_data = response.json()
                widget_id = None
                
                if 'value' in widget_data and 'id' in widget_data['value']:
                    widget_id = widget_data['value']['id']
                elif 'id' in widget_data:
                    widget_id = widget_data['id']
                
                if widget_id:
                    self.created_widgets.append({
                        'id': widget_id,
                        'text': sanitized_text[:50],
                        'position': (x, y),
                        'size': (width, height)
                    })
                    return True
            return False
        except Exception as e:
            print(f"Error creating widget: {str(e)}")
            return False
    
    def calculate_text_size(self, text, widget_type="standard"):
        """Calculate appropriate widget size based on text content"""
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        line_count = len(lines)
        
        # Size presets based on content
        if widget_type == "header":
            return (300, 80)
        elif widget_type == "body_part":
            return (150, 150)
        elif widget_type == "tdai":
            return (200, 120)
        elif widget_type == "detail":
            # Dynamic sizing for detailed content
            width = min(max(150, max_line_length * 6), 300)
            height = min(max(100, line_count * 25), 250)
            return (width, height)
        else:
            return (138, 138)  # Standard sticky note size
    
    def create_body_visualization(self):
        """Create anatomically positioned body parts"""
        print("\n📍 Creating Body Visualization...")
        
        body_parts = [
            ("HEAD\n\nCognitive Center", "HEAD"),
            ("HEART\n\nEmotional Core", "HEART"),
            ("TORSO\n\nCore Stability", "TORSO"),
            ("LEFT ARM\n\nAction", "LEFT_ARM"),
            ("RIGHT ARM\n\nCreation", "RIGHT_ARM"),
            ("LEFT LEG\n\nGrounding", "LEFT_LEG"),
            ("RIGHT LEG\n\nMovement", "RIGHT_LEG"),
        ]
        
        created = 0
        for text, part_type in body_parts:
            pos = self.layout_engine.get_anatomical_position(part_type)
            width, height = self.calculate_text_size(text, "body_part")
            
            if self.create_widget(text, pos.x, pos.y, width, height):
                created += 1
                print(f"  ✅ {part_type} at ({pos.x}, {pos.y})")
            
            time.sleep(0.3)  # Avoid rate limiting
        
        print(f"  Created {created}/{len(body_parts)} body parts")
        return created
    
    def create_tdai_scores(self):
        """Create TDAI score widgets with size-based severity indication"""
        print("\n📊 Creating TDAI Scores...")
        
        tdai_items = [
            ("CRITICAL ALERT\n━━━━━━━━━━━\nTDAI: 9.5\n\nImmediate attention\nrequired", 9.5),
            ("MODERATE CONCERN\n━━━━━━━━━━━\nTDAI: 6.0\n\nMonitor closely", 6.0),
            ("LOW PRIORITY\n━━━━━━━━━━━\nTDAI: 2.5\n\nRoutine check", 2.5),
        ]
        
        tdai_zone = self.layout_engine.get_zone_position("tdai")
        created = 0
        
        for i, (text, score) in enumerate(tdai_items):
            y_offset = i * 180
            
            # Larger size for higher severity
            if score >= 8:
                width, height = 220, 150
            elif score >= 5:
                width, height = 200, 130
            else:
                width, height = 180, 110
            
            if self.create_widget(text, tdai_zone.x, tdai_zone.y + y_offset, width, height):
                created += 1
                print(f"  ✅ TDAI {score} (size: {width}x{height})")
            
            time.sleep(0.3)
        
        print(f"  Created {created}/{len(tdai_items)} TDAI scores")
        return created
    
    def create_categories(self):
        """Create categorized content with spatial grouping"""
        print("\n📁 Creating Categories...")
        
        categories = {
            "THREATS": [
                "AI-Powered Detection",
                "Real-time Analysis",
                "Pattern Recognition"
            ],
            "COMPANIES": [
                "TechDefense GmbH",
                "AISecure Systems",
                "CyberShield Ltd"
            ],
            "EMOTIONS": [
                "Deep grief",
                "Unresolved anger",
                "Hidden fear"
            ],
            "GROUNDING": [
                "Safe space",
                "Present moment",
                "Body awareness"
            ]
        }
        
        cat_zone = self.layout_engine.get_zone_position("categories")
        created = 0
        y_offset = 0
        
        for category, items in categories.items():
            # Category header (larger)
            header_text = f"══ {category} ══"
            if self.create_widget(header_text, cat_zone.x, cat_zone.y + y_offset, 250, 60):
                created += 1
            
            y_offset += 70
            
            # Category items (smaller, indented)
            for item in items:
                if self.create_widget(f"• {item}", cat_zone.x + 20, cat_zone.y + y_offset, 180, 50):
                    created += 1
                y_offset += 60
                time.sleep(0.2)
            
            y_offset += 30  # Extra space between categories
        
        print(f"  Created {created} category widgets")
        return created
    
    def create_header_section(self):
        """Create header and legend"""
        print("\n📝 Creating Headers...")
        
        # Main header
        header_text = "MURAL VISUALIZATION\n" + "═" * 20 + "\nFormatted with Position & Size"
        header_zone = self.layout_engine.get_zone_position("header")
        
        created = 0
        if self.create_widget(header_text, header_zone.x, header_zone.y, 400, 100):
            created += 1
            print("  ✅ Main header created")
        
        # Information legend
        legend_items = [
            "LAYOUT LEGEND",
            "═══════════════",
            "• Position = Relationship",
            "• Size = Importance",
            "• Groups = Categories",
            "• Spacing = Separation",
        ]
        
        legend_text = '\n'.join(legend_items)
        if self.create_widget(legend_text, 50, 50, 200, 180):
            created += 1
            print("  ✅ Legend created")
        
        return created
    
    def create_complete_visualization(self):
        """Create the complete formatted visualization"""
        print("\n" + "="*70)
        print("CREATING FORMATTED MURAL VISUALIZATION")
        print("="*70)
        print(f"Board URL: https://app.mural.co/t/root7380/m/{self.board_id}")
        print("Note: All widgets will be yellow (API limitation)")
        print("Using position, size, and grouping for visual organization")
        print("-"*70)
        
        total_created = 0
        
        # Create all sections
        total_created += self.create_header_section()
        time.sleep(0.5)
        
        total_created += self.create_body_visualization()
        time.sleep(0.5)
        
        total_created += self.create_tdai_scores()
        time.sleep(0.5)
        
        total_created += self.create_categories()
        
        # Summary
        print("\n" + "="*70)
        print("VISUALIZATION COMPLETE!")
        print("="*70)
        print(f"Total widgets created: {total_created}")
        print(f"Widget details: {len(self.created_widgets)} tracked")
        
        print("\n📋 Created Elements:")
        for widget in self.created_widgets[:10]:  # Show first 10
            print(f"  • {widget['text']} at ({widget['position'][0]}, {widget['position'][1]})")
        
        if len(self.created_widgets) > 10:
            print(f"  ... and {len(self.created_widgets) - 10} more")
        
        print(f"\n🎯 View your board at:")
        print(f"   https://app.mural.co/t/root7380/m/{self.board_id}")
        
        print("\n✨ Visual Organization Achieved Through:")
        print("  • Anatomical positioning for body parts")
        print("  • Size hierarchy for importance (TDAI scores)")
        print("  • Spatial grouping for categories")
        print("  • Clear headers and legends")
        print("  • Strategic use of spacing")
        
        return total_created


if __name__ == "__main__":
    print("\n🚀 Starting MURAL Formatted Visualization")
    print("This implementation works within API limitations:")
    print("  ❌ No colors (not supported)")
    print("  ✅ Strategic positioning")
    print("  ✅ Dynamic sizing")
    print("  ✅ Spatial grouping")
    
    visualizer = MuralFormattedVisualization()
    total = visualizer.create_complete_visualization()
    
    if total > 0:
        print(f"\n✅ Successfully created {total} formatted widgets!")
        print("Check your MURAL board to see the organized visualization.")
    else:
        print("\n❌ No widgets were created. Check:")
        print("  1. OAuth token is valid")
        print("  2. Board ID is correct")
        print("  3. API is accessible")
