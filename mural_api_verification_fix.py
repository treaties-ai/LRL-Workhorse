#!/usr/bin/env python3
"""
MURAL API Verification and Layout Fix
Uses MURAL API to GET widget positions, detect overlaps, and fix layout
NO BROWSER AUTOMATION NEEDED - Pure API verification
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple
import math

# Load environment variables
load_dotenv('.env')

class MuralAPIVerifier:
    """Verify and fix widget positions using MURAL API"""
    
    def __init__(self):
        self.access_token = os.getenv('MURAL_ACCESS_TOKEN')
        self.workspace_id = "root7380"
        self.board_id = "1754493659737"
        self.combined_id = f"{self.workspace_id}.{self.board_id}"
        self.base_url = "https://app.mural.co/api/public/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Layout parameters based on visual feedback
        self.WIDGET_WIDTH = 200
        self.WIDGET_HEIGHT = 150
        self.HORIZONTAL_SPACING = 250  # Minimum spacing between widgets
        self.VERTICAL_SPACING = 200
        
        print("\n" + "="*80)
        print("MURAL API VERIFICATION AND FIX SYSTEM")
        print("="*80)
        print(f"Board: {self.combined_id}")
        print(f"API Endpoint: {self.base_url}")
        print("-"*80)
    
    def log(self, message, level="INFO"):
        """Enhanced logging with levels"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }
        print(f"[{timestamp}] {symbols.get(level, '•')} {message}")
    
    def get_all_widgets(self) -> List[Dict]:
        """Fetch all widgets from the board"""
        self.log("Fetching all widgets from board...", "INFO")
        
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                widgets = response.json().get('value', [])
                self.log(f"Found {len(widgets)} widgets on board", "SUCCESS")
                return widgets
            else:
                self.log(f"Failed to fetch widgets: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "DEBUG")
                return []
                
        except Exception as e:
            self.log(f"Error fetching widgets: {str(e)}", "ERROR")
            return []
    
    def analyze_widget_positions(self, widgets: List[Dict]) -> Dict:
        """Analyze widget positions and detect overlaps"""
        self.log("\n" + "="*60, "INFO")
        self.log("ANALYZING WIDGET POSITIONS", "INFO")
        self.log("="*60, "INFO")
        
        analysis = {
            "total_widgets": len(widgets),
            "overlapping_pairs": [],
            "position_map": {},
            "widgets_by_text": {}
        }
        
        # Log each widget's position
        for i, widget in enumerate(widgets):
            widget_id = widget.get('id', 'unknown')
            text = widget.get('text', '')[:30]  # First 30 chars
            x = widget.get('x', 0)
            y = widget.get('y', 0)
            width = widget.get('width', 0)
            height = widget.get('height', 0)
            
            self.log(f"Widget {i+1}: '{text}...' at ({x}, {y}) size: {width}x{height}", "DEBUG")
            
            analysis["position_map"][widget_id] = {
                "text": text,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            }
            
            # Group by text for duplicate detection
            if text not in analysis["widgets_by_text"]:
                analysis["widgets_by_text"][text] = []
            analysis["widgets_by_text"][text].append(widget_id)
        
        # Detect overlaps
        for i, w1 in enumerate(widgets):
            for j, w2 in enumerate(widgets[i+1:], i+1):
                if self.widgets_overlap(w1, w2):
                    analysis["overlapping_pairs"].append((
                        w1.get('id'),
                        w2.get('id'),
                        self.calculate_overlap_area(w1, w2)
                    ))
        
        # Report findings
        self.log(f"\nTotal widgets: {analysis['total_widgets']}", "INFO")
        self.log(f"Overlapping pairs: {len(analysis['overlapping_pairs'])}", 
                "WARNING" if analysis['overlapping_pairs'] else "SUCCESS")
        
        if analysis['overlapping_pairs']:
            self.log("\nOVERLAPPING WIDGETS DETECTED:", "WARNING")
            for id1, id2, area in analysis['overlapping_pairs'][:5]:  # Show first 5
                w1 = analysis["position_map"][id1]
                w2 = analysis["position_map"][id2]
                self.log(f"  '{w1['text']}' overlaps with '{w2['text']}' (area: {area}px²)", "WARNING")
        
        return analysis
    
    def widgets_overlap(self, w1: Dict, w2: Dict) -> bool:
        """Check if two widgets overlap"""
        x1, y1 = w1.get('x', 0), w1.get('y', 0)
        width1, height1 = w1.get('width', 100), w1.get('height', 100)
        
        x2, y2 = w2.get('x', 0), w2.get('y', 0)
        width2, height2 = w2.get('width', 100), w2.get('height', 100)
        
        # Check if rectangles overlap
        return not (x1 + width1 < x2 or x2 + width2 < x1 or
                   y1 + height1 < y2 or y2 + height2 < y1)
    
    def calculate_overlap_area(self, w1: Dict, w2: Dict) -> float:
        """Calculate overlapping area between two widgets"""
        x1, y1 = w1.get('x', 0), w1.get('y', 0)
        width1, height1 = w1.get('width', 100), w1.get('height', 100)
        
        x2, y2 = w2.get('x', 0), w2.get('y', 0)
        width2, height2 = w2.get('width', 100), w2.get('height', 100)
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + width1, x2 + width2) - max(x1, x2))
        y_overlap = max(0, min(y1 + height1, y2 + height2) - max(y1, y2))
        
        return x_overlap * y_overlap
    
    def calculate_proper_layout(self, widget_texts: List[str]) -> List[Tuple[str, int, int]]:
        """Calculate non-overlapping positions for widgets"""
        self.log("\n" + "="*60, "INFO")
        self.log("CALCULATING PROPER LAYOUT", "INFO")
        self.log("="*60, "INFO")
        
        layout = []
        
        # Body parts - anatomical positioning
        body_parts = {
            "Right Eye Twitching": (500, 200),
            "Dry Eyes": (700, 200),
            "Left Arm Tingling": (300, 400),
            "Esophageal Tightness": (500, 400),
            "Right Arm Tingling": (700, 400),
            "Dry Lungs": (500, 500),
            "Epigastric Coldness": (500, 600),
            "Left Hip Pain": (300, 700),
            "Right Hip Pain": (700, 700),
            "Calf Muscle Tingling": (500, 900),
        }
        
        # Categories with grid layout
        categories = {
            "TDAI Metrics": (1000, 200),
            "Neural": (1300, 200),
            "Respiratory": (1000, 400),
            "Gastrointestinal": (1300, 400),
            "Musculoskeletal": (1000, 600),
            "Visual": (1300, 600),
            "Energetic": (1000, 800),
            "Overall Pattern": (1300, 800),
        }
        
        # TDAI scores - sized by severity
        tdai_scores = {
            "Overall TDAI 7": (1600, 300),
            "Regional Scores": (1600, 500),
            "Severity Pattern": (1600, 700),
        }
        
        # Start positions for different groups
        current_x = 100
        current_y = 200
        
        for text in widget_texts:
            # Check if it's a known category
            placed = False
            
            # Check body parts
            for key, (x, y) in body_parts.items():
                if key.lower() in text.lower():
                    layout.append((text, x, y))
                    self.log(f"Placing '{text[:30]}' at anatomical position ({x}, {y})", "SUCCESS")
                    placed = True
                    break
            
            # Check categories
            if not placed:
                for key, (x, y) in categories.items():
                    if key.lower() in text.lower():
                        layout.append((text, x, y))
                        self.log(f"Placing '{text[:30]}' in category area ({x}, {y})", "SUCCESS")
                        placed = True
                        break
            
            # Check TDAI
            if not placed:
                for key, (x, y) in tdai_scores.items():
                    if "tdai" in text.lower() or "score" in text.lower():
                        layout.append((text, x, y))
                        self.log(f"Placing '{text[:30]}' in TDAI area ({x}, {y})", "SUCCESS")
                        placed = True
                        break
            
            # Default grid placement
            if not placed:
                layout.append((text, current_x, current_y))
                self.log(f"Placing '{text[:30]}' at grid position ({current_x}, {current_y})", "INFO")
                
                # Move to next position
                current_x += self.HORIZONTAL_SPACING
                if current_x > 2000:
                    current_x = 100
                    current_y += self.VERTICAL_SPACING
        
        return layout
    
    def delete_widget(self, widget_id: str) -> bool:
        """Delete a widget from the board"""
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/{widget_id}"
        
        try:
            response = requests.delete(endpoint, headers=self.headers, timeout=10)
            return response.status_code in [200, 204]
        except Exception as e:
            self.log(f"Error deleting widget {widget_id}: {str(e)}", "ERROR")
            return False
    
    def create_widget(self, text: str, x: int, y: int) -> bool:
        """Create a new widget at specified position"""
        from mural_working_test import sanitize_for_mural_display
        
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/sticky-note"
        sanitized_text = sanitize_for_mural_display(text)
        
        payload = {
            "shape": "rectangle",
            "text": sanitized_text,
            "x": x,
            "y": y,
            "width": self.WIDGET_WIDTH,
            "height": self.WIDGET_HEIGHT
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            return response.status_code in [200, 201]
        except Exception as e:
            self.log(f"Error creating widget: {str(e)}", "ERROR")
            return False
    
    def fix_overlapping_layout(self):
        """Main function to fix overlapping widgets"""
        self.log("\n" + "="*80, "INFO")
        self.log("STARTING LAYOUT FIX PROCESS", "INFO")
        self.log("="*80, "INFO")
        
        # Step 1: Get all widgets
        widgets = self.get_all_widgets()
        if not widgets:
            self.log("No widgets found or error fetching", "ERROR")
            return
        
        # Step 2: Analyze positions
        analysis = self.analyze_widget_positions(widgets)
        
        # Step 3: If overlaps exist, fix them
        if analysis["overlapping_pairs"]:
            self.log("\n" + "="*60, "WARNING")
            self.log("FIXING OVERLAPPING WIDGETS", "WARNING")
            self.log("="*60, "WARNING")
            
            # Get all widget texts
            widget_texts = [w.get('text', '') for w in widgets]
            
            # Calculate proper layout
            proper_layout = self.calculate_proper_layout(widget_texts)
            
            # Option 1: Delete all and recreate (cleaner)
            self.log("\nDeleting overlapping widgets...", "INFO")
            deleted_count = 0
            for widget in widgets:
                if self.delete_widget(widget.get('id')):
                    deleted_count += 1
            
            self.log(f"Deleted {deleted_count} widgets", "SUCCESS")
            
            # Recreate with proper positions
            self.log("\nCreating widgets with proper layout...", "INFO")
            created_count = 0
            for text, x, y in proper_layout:
                if self.create_widget(text, x, y):
                    created_count += 1
                    self.log(f"Created: '{text[:30]}' at ({x}, {y})", "SUCCESS")
                time.sleep(0.1)  # Small delay to avoid rate limiting
            
            self.log(f"\nCreated {created_count} widgets with proper spacing", "SUCCESS")
            
            # Step 4: Verify the fix
            self.log("\nVerifying fixed layout...", "INFO")
            time.sleep(2)  # Wait for API to update
            
            new_widgets = self.get_all_widgets()
            new_analysis = self.analyze_widget_positions(new_widgets)
            
            if not new_analysis["overlapping_pairs"]:
                self.log("\n🎉 SUCCESS! All overlaps have been fixed!", "SUCCESS")
                self.log(f"Board now has {len(new_widgets)} properly positioned widgets", "SUCCESS")
            else:
                self.log(f"\n⚠️ Still have {len(new_analysis['overlapping_pairs'])} overlaps", "WARNING")
        else:
            self.log("\n✅ No overlapping widgets detected - layout is already good!", "SUCCESS")
        
        # Final board link
        visitor_link = "https://app.mural.co/t/root7380/m/root7380/1754493659737/b1fb80b8346bc1f088585d4541944c1707089c44"
        self.log(f"\nView the board: {visitor_link}", "INFO")


def main():
    """Main execution"""
    verifier = MuralAPIVerifier()
    verifier.fix_overlapping_layout()


if __name__ == "__main__":
    main()
