#!/usr/bin/env python3
"""
MURAL Visual Formatter V2 - Enhanced with Collision Detection and Spacing Management
Prevents widget overlapping and ensures proper spacing between all elements
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass

# Load environment variables
load_dotenv('.env')

@dataclass
class WidgetBounds:
    """Represents the boundaries of a widget"""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def left(self) -> int:
        return self.x
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def top(self) -> int:
        return self.y
    
    @property
    def bottom(self) -> int:
        return self.y + self.height
    
    def overlaps_with(self, other: 'WidgetBounds', buffer: int = 20) -> bool:
        """Check if this widget overlaps with another (including buffer zone)"""
        # Add buffer to create spacing between widgets
        return not (self.right + buffer < other.left or 
                   self.left > other.right + buffer or 
                   self.bottom + buffer < other.top or 
                   self.top > other.bottom + buffer)
    
    def distance_to(self, other: 'WidgetBounds') -> float:
        """Calculate distance between widget centers"""
        center_x1 = self.x + self.width / 2
        center_y1 = self.y + self.height / 2
        center_x2 = other.x + other.width / 2
        center_y2 = other.y + other.height / 2
        return ((center_x2 - center_x1) ** 2 + (center_y2 - center_y1) ** 2) ** 0.5

class VisualCategory(Enum):
    """Visual categories using emojis for color simulation"""
    START = "🟢"      # Green - Starting points
    PROCESS = "⚡"    # Lightning - Active processes
    COMPLETE = "✅"   # Checkmark - Completed items
    WARNING = "⚠️"    # Warning - Attention needed
    ERROR = "❌"      # Error - Problems
    INFO = "🔵"       # Blue - Information
    IDEA = "💡"       # Lightbulb - Ideas
    GOAL = "🎯"      # Target - Goals
    PRIORITY = "⭐"   # Star - High priority
    QUESTION = "❓"   # Question mark
    DECISION = "🔀"   # Fork - Decision points
    DOCUMENT = "📄"   # Document
    TEAM = "👥"       # Team/People
    TIME = "⏰"       # Time-sensitive
    MONEY = "💰"      # Budget/Financial
    
class WidgetSize(Enum):
    """Predefined widget sizes for visual hierarchy"""
    HERO = (300, 120)        # Large headers
    SECTION = (250, 100)     # Section headers
    STANDARD = (200, 150)    # Normal content
    COMPACT = (150, 100)     # Smaller items
    CONNECTOR = (80, 40)     # Arrow connectors
    ANNOTATION = (120, 80)   # Small notes
    WIDE = (350, 80)        # Wide banners
    TALL = (150, 200)       # Tall cards

class LayoutZone(Enum):
    """Predefined zones for different layout types"""
    PROCESS_FLOW = (0, 0, 1600, 400)        # Top area
    MIND_MAP = (400, 400, 1200, 800)        # Center area
    KANBAN = (0, 800, 1200, 1400)           # Bottom area
    DECISION_TREE = (1200, 0, 1800, 600)    # Right top area
    NETWORK = (1200, 600, 1800, 1200)       # Right bottom area
    FREE_ZONE = (1800, 0, 2400, 1400)       # Extra space

class WidgetRegistry:
    """Tracks all placed widgets to prevent overlaps"""
    
    def __init__(self):
        self.widgets: List[WidgetBounds] = []
        self.min_spacing = 30  # Minimum pixels between widgets
        
    def register(self, bounds: WidgetBounds) -> None:
        """Register a new widget placement"""
        self.widgets.append(bounds)
        
    def check_collision(self, new_bounds: WidgetBounds) -> bool:
        """Check if new widget would collide with existing ones"""
        for existing in self.widgets:
            if existing.overlaps_with(new_bounds, self.min_spacing):
                return True
        return False
    
    def find_safe_position(self, desired_x: int, desired_y: int, 
                          width: int, height: int, 
                          search_radius: int = 500) -> Tuple[int, int]:
        """Find nearest safe position for widget placement"""
        new_bounds = WidgetBounds(desired_x, desired_y, width, height)
        
        # If position is safe, use it
        if not self.check_collision(new_bounds):
            return desired_x, desired_y
        
        # Search in expanding circles for safe position
        for radius in range(50, search_radius, 50):
            # Try positions in a circle around desired point
            for angle in range(0, 360, 30):
                import math
                rad = math.radians(angle)
                test_x = int(desired_x + radius * math.cos(rad))
                test_y = int(desired_y + radius * math.sin(rad))
                
                test_bounds = WidgetBounds(test_x, test_y, width, height)
                if not self.check_collision(test_bounds):
                    return test_x, test_y
        
        # If no safe position found, offset significantly
        offset_x = desired_x + search_radius
        offset_y = desired_y
        return offset_x, offset_y
    
    def clear(self) -> None:
        """Clear the registry"""
        self.widgets = []
    
    def get_zone_widgets(self, zone: LayoutZone) -> List[WidgetBounds]:
        """Get all widgets in a specific zone"""
        x_min, y_min, x_max, y_max = zone.value
        zone_widgets = []
        for widget in self.widgets:
            if (x_min <= widget.x <= x_max and y_min <= widget.y <= y_max):
                zone_widgets.append(widget)
        return zone_widgets

class MuralVisualFormatterV2:
    """Enhanced formatter with collision detection and spacing management"""
    
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
        
        # Widget registry for collision detection
        self.registry = WidgetRegistry()
        
        # Enhanced spacing parameters
        self.MIN_WIDGET_SPACING = 40    # Minimum space between any widgets
        self.ARROW_SPACING = 30          # Space for arrow connectors
        self.GROUP_SPACING = 100         # Space between widget groups
        self.ZONE_PADDING = 50           # Padding within zones
        
        print("\n" + "="*80)
        print("🎨 MURAL Visual Formatter V2 - With Collision Detection")
        print("="*80)
        print("Features: No overlapping, proper spacing, zone management")
        print(f"Board: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}")
        print("-"*80)
    
    def log(self, message, level="INFO"):
        """Enhanced logging with emojis"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "VISUAL": "🎨",
            "CONNECT": "🔗",
            "LAYOUT": "📐",
            "COLLISION": "⚠️",
            "SPACING": "📏"
        }
        print(f"[{timestamp}] {symbols.get(level, '•')} {message}")
    
    def sanitize_for_api(self, text: str) -> str:
        """Remove problematic Unicode characters while preserving emojis"""
        replacements = {
            '━': '─', '─': '-', '│': '|',
            '€': 'EUR', '™': 'TM', '®': '(R)',
            '"': '"', '"': '"', ''': "'", ''': "'"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = ''.join(char for char in text if ord(char) >= 32 or ord(char) > 127000)
        return text
    
    def create_widget(self, text: str, x: int, y: int, 
                     size: WidgetSize = WidgetSize.STANDARD,
                     category: Optional[VisualCategory] = None,
                     check_collision: bool = True) -> bool:
        """Create a widget with collision detection"""
        
        # Add category emoji if specified
        if category:
            text = f"{category.value} {text}"
        
        width, height = size.value
        
        # Check for collisions and find safe position if needed
        if check_collision:
            safe_x, safe_y = self.registry.find_safe_position(x, y, width, height)
            if safe_x != x or safe_y != y:
                self.log(f"Collision detected at ({x}, {y}), moved to ({safe_x}, {safe_y})", "COLLISION")
                x, y = safe_x, safe_y
        
        # Register the widget bounds
        bounds = WidgetBounds(x, y, width, height)
        self.registry.register(bounds)
        
        # Create the widget via API
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/sticky-note"
        
        payload = {
            "shape": "rectangle",
            "text": self.sanitize_for_api(text),
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                self.log(f"Created: '{text[:30]}...' at ({x}, {y})", "SUCCESS")
                return True
            else:
                self.log(f"Failed to create widget: {response.status_code}", "ERROR")
                # Remove from registry if creation failed
                self.registry.widgets.pop()
                return False
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            # Remove from registry if creation failed
            self.registry.widgets.pop()
            return False
    
    def create_arrow_connector(self, x: int, y: int, direction: str = "→") -> bool:
        """Create a small arrow widget to show connections"""
        return self.create_widget(direction, x, y, WidgetSize.CONNECTOR)
    
    def clear_board(self):
        """Clear all existing widgets from the board"""
        self.log("Clearing existing widgets...", "INFO")
        
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets"
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            widgets = response.json().get('value', [])
            self.log(f"Found {len(widgets)} widgets to delete", "INFO")
            
            for widget in widgets:
                widget_id = widget.get('id')
                delete_endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/{widget_id}"
                requests.delete(delete_endpoint, headers=self.headers)
            
            self.log("Board cleared", "SUCCESS")
            # Clear the registry as well
            self.registry.clear()
    
    def get_zone_start_position(self, zone: LayoutZone) -> Tuple[int, int]:
        """Get the starting position for a layout zone with padding"""
        x_min, y_min, x_max, y_max = zone.value
        return x_min + self.ZONE_PADDING, y_min + self.ZONE_PADDING
    
    # ===== IMPROVED LAYOUT TEMPLATES =====
    
    def create_process_flow(self, steps: List[Dict], zone: Optional[LayoutZone] = None):
        """Create a horizontal process flow with proper spacing"""
        self.log("Creating Process Flow Layout with collision detection", "LAYOUT")
        
        # Use specified zone or default
        if zone:
            start_x, start_y = self.get_zone_start_position(zone)
        else:
            start_x, start_y = 100, 200
        
        current_x = start_x
        
        for i, step in enumerate(steps):
            category = step.get("category", VisualCategory.PROCESS)
            size = WidgetSize.SECTION if i == 0 else WidgetSize.STANDARD
            width, height = size.value
            
            # Create the main step widget
            self.create_widget(
                step["text"],
                current_x,
                start_y,
                size=size,
                category=category
            )
            
            # Add arrow connector (except after last step)
            if i < len(steps) - 1:
                # Calculate arrow position with proper spacing
                arrow_x = current_x + width + self.ARROW_SPACING
                arrow_y = start_y + (height // 2) - 20
                self.create_arrow_connector(arrow_x, arrow_y, "→")
                
                # Move to next position with adequate spacing
                connector_width = WidgetSize.CONNECTOR.value[0]
                current_x = arrow_x + connector_width + self.MIN_WIDGET_SPACING
            
            time.sleep(0.2)
    
    def create_mind_map(self, center: str, branches: Dict[str, List[str]], 
                       zone: Optional[LayoutZone] = None):
        """Create a mind map with proper spacing and no overlaps"""
        self.log("Creating Mind Map Layout with collision detection", "LAYOUT")
        
        # Use specified zone or calculate center
        if zone:
            x_min, y_min, x_max, y_max = zone.value
            start_x = (x_min + x_max) // 2 - 150
            start_y = (y_min + y_max) // 2 - 60
        else:
            start_x, start_y = 500, 400
        
        # Create central node
        self.create_widget(
            center,
            start_x,
            start_y,
            size=WidgetSize.HERO,
            category=VisualCategory.IDEA
        )
        
        # Calculate branch positions with better spacing
        center_width, center_height = WidgetSize.HERO.value
        
        positions = {
            "north": (start_x + center_width//2 - 75, start_y - 250, "↑"),
            "east": (start_x + center_width + 150, start_y + center_height//2 - 50, "→"),
            "south": (start_x + center_width//2 - 75, start_y + center_height + 150, "↓"),
            "west": (start_x - 250, start_y + center_height//2 - 50, "←")
        }
        
        for direction, items in branches.items():
            if direction in positions:
                branch_x, branch_y, arrow = positions[direction]
                
                # Add connector arrow with proper positioning
                if direction == "north":
                    arrow_x = start_x + center_width//2 - 40
                    arrow_y = start_y - 60
                elif direction == "south":
                    arrow_x = start_x + center_width//2 - 40
                    arrow_y = start_y + center_height + 20
                elif direction == "east":
                    arrow_x = start_x + center_width + 20
                    arrow_y = start_y + center_height//2 - 20
                else:  # west
                    arrow_x = start_x - 100
                    arrow_y = start_y + center_height//2 - 20
                
                self.create_arrow_connector(arrow_x, arrow_y, arrow)
                
                # Add branch items with proper spacing
                for i, item in enumerate(items):
                    item_y = branch_y + (i * 140)  # Increased spacing
                    self.create_widget(
                        item,
                        branch_x,
                        item_y,
                        size=WidgetSize.COMPACT,
                        category=VisualCategory.INFO
                    )
                
                time.sleep(0.3)
    
    def create_kanban_board(self, columns: Dict[str, List[str]], 
                           zone: Optional[LayoutZone] = None):
        """Create a Kanban-style board with proper column spacing"""
        self.log("Creating Kanban Board Layout with collision detection", "LAYOUT")
        
        if zone:
            start_x, start_y = self.get_zone_start_position(zone)
        else:
            start_x, start_y = 100, 150
        
        column_categories = {
            "To Do": VisualCategory.QUESTION,
            "In Progress": VisualCategory.PROCESS,
            "Done": VisualCategory.COMPLETE,
            "Backlog": VisualCategory.TIME,
            "Review": VisualCategory.DOCUMENT
        }
        
        # Calculate column width based on widget size and spacing
        column_width = WidgetSize.SECTION.value[0]
        column_spacing = column_width + self.GROUP_SPACING
        
        for col_idx, (col_name, tasks) in enumerate(columns.items()):
            col_x = start_x + (col_idx * column_spacing)
            
            # Column header
            category = column_categories.get(col_name, VisualCategory.INFO)
            self.create_widget(
                col_name,
                col_x,
                start_y,
                size=WidgetSize.SECTION,
                category=category
            )
            
            # Tasks in column with proper spacing
            task_y = start_y + WidgetSize.SECTION.value[1] + self.MIN_WIDGET_SPACING
            
            for task in tasks:
                self.create_widget(
                    task,
                    col_x,
                    task_y,
                    size=WidgetSize.COMPACT,
                    category=None
                )
                task_y += WidgetSize.COMPACT.value[1] + self.MIN_WIDGET_SPACING
            
            time.sleep(0.3)
    
    def create_decision_tree(self, question: str, branches: List[Dict],
                            zone: Optional[LayoutZone] = None):
        """Create a decision tree with proper spacing"""
        self.log("Creating Decision Tree Layout with collision detection", "LAYOUT")
        
        if zone:
            x_min, y_min, x_max, y_max = zone.value
            start_x = (x_min + x_max) // 2 - 125
            start_y = y_min + self.ZONE_PADDING
        else:
            start_x, start_y = 400, 150
        
        # Main question
        self.create_widget(
            question,
            start_x,
            start_y,
            size=WidgetSize.SECTION,
            category=VisualCategory.QUESTION
        )
        
        question_width, question_height = WidgetSize.SECTION.value
        
        # Branch arrows with better positioning
        arrow_y = start_y + question_height + self.ARROW_SPACING
        left_arrow_x = start_x + 20
        right_arrow_x = start_x + question_width - 100
        
        self.create_arrow_connector(left_arrow_x, arrow_y, "↙")
        self.create_arrow_connector(right_arrow_x, arrow_y, "↘")
        
        # Branches with adequate spacing
        branch_y = arrow_y + WidgetSize.CONNECTOR.value[1] + self.MIN_WIDGET_SPACING
        
        for i, branch in enumerate(branches[:2]):
            # Position branches with good separation
            if i == 0:  # Left branch
                branch_x = start_x - 150
            else:  # Right branch
                branch_x = start_x + question_width + 50
            
            # Condition
            condition_category = VisualCategory.COMPLETE if branch["condition"] in ["Yes", "Approve"] else VisualCategory.ERROR
            self.create_widget(
                branch["condition"],
                branch_x,
                branch_y,
                size=WidgetSize.ANNOTATION,
                category=condition_category
            )
            
            # Outcome with spacing
            outcome_y = branch_y + WidgetSize.ANNOTATION.value[1] + self.MIN_WIDGET_SPACING
            self.create_widget(
                branch["outcome"],
                branch_x,
                outcome_y,
                size=WidgetSize.STANDARD,
                category=VisualCategory.GOAL
            )
            
            time.sleep(0.2)
    
    def demo_with_zones(self):
        """Demonstrate all layouts in their designated zones"""
        self.log("\n🎨 Running Zoned Layout Demo", "VISUAL")
        
        # Clear board first
        self.clear_board()
        time.sleep(2)
        
        # 1. Process Flow in top zone
        self.log("\n1️⃣ Creating Process Flow in designated zone", "VISUAL")
        process_steps = [
            {"text": "Start", "category": VisualCategory.START},
            {"text": "Process", "category": VisualCategory.PROCESS},
            {"text": "Complete", "category": VisualCategory.COMPLETE}
        ]
        self.create_process_flow(process_steps, LayoutZone.PROCESS_FLOW)
        
        # 2. Mind Map in center zone
        self.log("\n2️⃣ Creating Mind Map in designated zone", "VISUAL")
        branches = {
            "north": ["Goal"],
            "east": ["Task"],
            "south": ["Risk"],
            "west": ["Team"]
        }
        self.create_mind_map("Central Hub", branches, LayoutZone.MIND_MAP)
        
        # 3. Kanban in bottom zone
        self.log("\n3️⃣ Creating Kanban Board in designated zone", "VISUAL")
        kanban_columns = {
            "To Do": ["Task 1", "Task 2"],
            "In Progress": ["Task 3"],
            "Done": ["Task 4"]
        }
        self.create_kanban_board(kanban_columns, LayoutZone.KANBAN)
        
        # 4. Decision Tree in right zone
        self.log("\n4️⃣ Creating Decision Tree in designated zone", "VISUAL")
        decision_branches = [
            {"condition": "Yes", "outcome": "Proceed"},
            {"condition": "No", "outcome": "Stop"}
        ]
        self.create_decision_tree("Continue?", decision_branches, LayoutZone.DECISION_TREE)
        
        self.log("\n✅ Zoned layout complete with no overlaps!", "SUCCESS")
        self.log(f"View your board: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}", "INFO")


def main():
    """Main execution"""
    formatter = MuralVisualFormatterV2()
    
    print("\n" + "="*80)
    print("MURAL Visual Formatter V2 - Quality Assured Demo")
    print("="*80)
    print("\nThis version includes:")
    print("✅ Collision detection")
    print("✅ Automatic spacing adjustment")
    print("✅ Zone management")
    print("✅ No overlapping widgets")
    print("-"*80)
    
    # Run the zoned demo
    formatter.demo_with_zones()


if __name__ == "__main__":
    main()
