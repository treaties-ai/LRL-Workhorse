#!/usr/bin/env python3
"""
MURAL Color Manager - Handles color schemes and PATCH operations for widget styling
Based on the discovery that colors must be applied AFTER widget creation via PATCH
"""

import requests
import os
import json
import time
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class MuralColorManager:
    """Manages color schemes and applies colors to MURAL widgets via PATCH operations"""
    
    # Color schemes based on content types
    COLOR_SCHEMES = {
        # Body Parts - Anatomical visualization
        "HEAD": "#4A90E2",      # Blue
        "HEART": "#E94B3C",     # Red  
        "TORSO": "#6B5B95",     # Purple
        "ARMS": "#F0AD4E",      # Orange
        "LEGS": "#5CB85C",      # Green
        "LEFT_ARM": "#F0AD4E",  # Orange (same as ARMS)
        "RIGHT_ARM": "#F0AD4E", # Orange
        "LEFT_LEG": "#5CB85C",  # Green (same as LEGS)
        "RIGHT_LEG": "#5CB85C", # Green
        
        # TDAI Score-based colors
        "TDAI_HIGH": "#D32F2F",     # Dark Red (8-10)
        "TDAI_MEDIUM": "#FFA726",   # Orange (5-7)  
        "TDAI_LOW": "#66BB6A",      # Green (0-4)
        
        # Content Categories
        "THREAT": "#B71C1C",        # Deep Red
        "COMPANY": "#1565C0",       # Deep Blue
        "EMOTION": "#7B1FA2",       # Deep Purple
        "GROUNDING": "#2E7D32",     # Deep Green
        "HEADER": "#424242",        # Dark Gray
        "DEFAULT": "#FFEB3B",       # Yellow (fallback)
    }
    
    def __init__(self):
        """Initialize the color manager with API credentials"""
        self.access_token = os.getenv('MURAL_ACCESS_TOKEN')
        # The MURAL_BOARD_ID in .env already contains the full format "root7380.1754493659737"
        full_board_id = os.getenv('MURAL_BOARD_ID', 'root7380.1754493659737')
        
        # Split it to get workspace and board separately if needed
        if '.' in full_board_id:
            self.workspace_id, self.board_id = full_board_id.split('.', 1)
        else:
            self.workspace_id = 'root7380'
            self.board_id = full_board_id
        
        self.base_url = "https://app.mural.co/api/public/v1"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Track widget IDs for batch operations
        self.widget_registry = {}
        
    def get_color_for_content(self, text: str, content_type: Optional[str] = None) -> str:
        """
        Determine the appropriate color based on content type or text analysis
        
        Args:
            text: The widget text content
            content_type: Optional explicit content type
            
        Returns:
            Hex color code string
        """
        # If explicit type provided, use it
        if content_type and content_type.upper() in self.COLOR_SCHEMES:
            return self.COLOR_SCHEMES[content_type.upper()]
        
        # Analyze text to determine type
        text_upper = text.upper()
        
        # Check for body parts
        body_parts = ["HEAD", "HEART", "TORSO", "ARM", "LEG", "LEFT_ARM", "RIGHT_ARM", "LEFT_LEG", "RIGHT_LEG"]
        for part in body_parts:
            if part in text_upper:
                return self.COLOR_SCHEMES.get(part, self.COLOR_SCHEMES["DEFAULT"])
        
        # Check for TDAI scores
        if "TDAI" in text_upper:
            score = self._extract_tdai_score(text)
            if score is not None:
                if score >= 8:
                    return self.COLOR_SCHEMES["TDAI_HIGH"]
                elif score >= 5:
                    return self.COLOR_SCHEMES["TDAI_MEDIUM"]
                else:
                    return self.COLOR_SCHEMES["TDAI_LOW"]
        
        # Check for category keywords
        if any(word in text_upper for word in ["THREAT", "RISK", "DANGER"]):
            return self.COLOR_SCHEMES["THREAT"]
        elif any(word in text_upper for word in ["COMPANY", "CORP", "BUSINESS", "LTD", "GMBH"]):
            return self.COLOR_SCHEMES["COMPANY"]
        elif any(word in text_upper for word in ["EMOTION", "FEEL", "GRIEF", "ANGER", "FEAR"]):
            return self.COLOR_SCHEMES["EMOTION"]
        elif any(word in text_upper for word in ["GROUND", "SAFE", "SECURE", "STABLE"]):
            return self.COLOR_SCHEMES["GROUNDING"]
        
        # Default color
        return self.COLOR_SCHEMES["DEFAULT"]
    
    def _extract_tdai_score(self, text: str) -> Optional[float]:
        """Extract TDAI score from text if present"""
        import re
        # Look for patterns like "TDAI: 8.5" or "TDAI Score: 7"
        patterns = [
            r'TDAI[:\s]+([0-9]+\.?[0-9]*)',
            r'Score[:\s]+([0-9]+\.?[0-9]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
    
    def patch_widget_color(self, widget_id: str, color: str) -> bool:
        """
        Apply color to an existing widget using PATCH
        
        Args:
            widget_id: The ID of the widget to update
            color: Hex color code
            
        Returns:
            True if successful, False otherwise
        """
        # Construct the PATCH endpoint - use the full board ID from env
        combined_id = os.getenv('MURAL_BOARD_ID', 'root7380.1754493659737')
        patch_url = f"{self.base_url}/murals/{combined_id}/widgets/{widget_id}"
        
        # Payload for color update
        patch_payload = {
            "style": {
                "backgroundColor": color
            }
        }
        
        try:
            response = requests.patch(
                patch_url,
                headers=self.headers,
                json=patch_payload,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Successfully colored widget {widget_id} with {color}")
                return True
            else:
                print(f"❌ Failed to color widget {widget_id}: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"💥 Error patching widget {widget_id}: {str(e)}")
            return False
    
    def create_and_color_widget(self, text: str, x: int, y: int, 
                               width: int = 138, height: int = 138,
                               content_type: Optional[str] = None) -> Optional[str]:
        """
        Create a widget and immediately apply color based on content
        
        Args:
            text: Widget text content (will be sanitized)
            x, y: Position coordinates
            width, height: Widget dimensions
            content_type: Optional explicit content type
            
        Returns:
            Widget ID if successful, None otherwise
        """
        from mural_working_test import sanitize_for_mural_display
        
        # Sanitize text
        sanitized_text = sanitize_for_mural_display(text)
        
        # Create the widget - use the full board ID from env
        combined_id = os.getenv('MURAL_BOARD_ID', 'root7380.1754493659737')
        create_url = f"{self.base_url}/murals/{combined_id}/widgets/sticky-note"
        
        create_payload = {
            "shape": "rectangle",
            "text": sanitized_text,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        try:
            # Step 1: Create the widget
            response = requests.post(
                create_url,
                headers=self.headers,
                json=create_payload,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Failed to create widget: {response.status_code}")
                return None
            
            # Extract widget ID from response
            response_data = response.json()
            widget_id = None
            
            # Try different response structures
            if 'value' in response_data and 'id' in response_data['value']:
                widget_id = response_data['value']['id']
            elif 'id' in response_data:
                widget_id = response_data['id']
            elif 'data' in response_data and 'id' in response_data['data']:
                widget_id = response_data['data']['id']
            
            if not widget_id:
                print("⚠️ Created widget but couldn't extract ID for coloring")
                print(f"   Response structure: {json.dumps(response_data, indent=2)[:500]}")
                return None
            
            print(f"✅ Created widget {widget_id}")
            
            # Step 2: Apply color
            color = self.get_color_for_content(text, content_type)
            
            # Small delay to ensure widget is ready
            time.sleep(0.2)
            
            if self.patch_widget_color(widget_id, color):
                # Store in registry for tracking
                self.widget_registry[widget_id] = {
                    'text': sanitized_text,
                    'color': color,
                    'type': content_type or 'auto-detected',
                    'position': (x, y)
                }
                return widget_id
            else:
                print(f"⚠️ Widget created but coloring failed for {widget_id}")
                return widget_id
                
        except Exception as e:
            print(f"💥 Error in create_and_color_widget: {str(e)}")
            return None
    
    def batch_color_update(self, widget_color_map: Dict[str, str]) -> Dict[str, bool]:
        """
        Update colors for multiple widgets
        
        Args:
            widget_color_map: Dict mapping widget IDs to color codes
            
        Returns:
            Dict mapping widget IDs to success status
        """
        results = {}
        
        for widget_id, color in widget_color_map.items():
            # Add small delay between requests to avoid rate limiting
            time.sleep(0.3)
            results[widget_id] = self.patch_widget_color(widget_id, color)
            
        return results
    
    def create_color_legend(self, x: int = 50, y: int = 50) -> None:
        """Create a color legend showing all color mappings"""
        legend_items = [
            ("COLOR LEGEND", "HEADER"),
            ("Body Parts", "HEAD"),
            ("TDAI High (8-10)", "TDAI_HIGH"),
            ("TDAI Medium (5-7)", "TDAI_MEDIUM"),
            ("TDAI Low (0-4)", "TDAI_LOW"),
            ("Threats", "THREAT"),
            ("Companies", "COMPANY"),
            ("Emotions", "EMOTION"),
            ("Grounding", "GROUNDING"),
        ]
        
        current_y = y
        for label, color_key in legend_items:
            self.create_and_color_widget(
                text=label,
                x=x,
                y=current_y,
                width=150,
                height=50,
                content_type=color_key
            )
            current_y += 60
            time.sleep(0.5)  # Avoid rate limiting
    
    def get_widget_stats(self) -> Dict:
        """Get statistics about created and colored widgets"""
        stats = {
            "total_widgets": len(self.widget_registry),
            "by_type": {},
            "by_color": {}
        }
        
        for widget_data in self.widget_registry.values():
            # Count by type
            widget_type = widget_data['type']
            stats["by_type"][widget_type] = stats["by_type"].get(widget_type, 0) + 1
            
            # Count by color
            color = widget_data['color']
            stats["by_color"][color] = stats["by_color"].get(color, 0) + 1
        
        return stats


# Test function for standalone execution
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MURAL COLOR MANAGER TEST")
    print("="*70)
    
    manager = MuralColorManager()
    
    print("\n1. Testing color detection:")
    test_texts = [
        ("HEAD", None),
        ("TDAI: 9.5 - Critical", None),
        ("TechDefense GmbH", None),
        ("Deep grief in chest", None),
        ("Grounded and safe", None),
    ]
    
    for text, content_type in test_texts:
        color = manager.get_color_for_content(text, content_type)
        print(f"   '{text}' -> {color}")
    
    print("\n2. Testing widget creation with color:")
    test_widget_id = manager.create_and_color_widget(
        text="COLOR TEST - TDAI: 8.5",
        x=900,
        y=100,
        content_type=None  # Let it auto-detect
    )
    
    if test_widget_id:
        print(f"   Created and colored widget: {test_widget_id}")
    
    print("\n3. Widget statistics:")
    stats = manager.get_widget_stats()
    print(f"   {json.dumps(stats, indent=2)}")
    
    print("\n✅ Color manager test complete!")
