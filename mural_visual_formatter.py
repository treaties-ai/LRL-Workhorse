#!/usr/bin/env python3
"""
MURAL Visual Formatter - Enhanced with Visual Variation and Connections
Creates visually interesting MURAL boards with emojis, size hierarchy, and visual connections
Works within API constraints (no color changes, no actual lines)
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional
from enum import Enum

# Load environment variables
load_dotenv('.env')

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

class MuralVisualFormatter:
    """Enhanced formatter with visual variation and connections"""
    
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
        
        # Layout parameters
        self.TIGHT_SPACING = 150    # For connected items
        self.NORMAL_SPACING = 250   # Standard spacing
        self.WIDE_SPACING = 400     # Between groups
        
        print("\n" + "="*80)
        print("🎨 MURAL Visual Formatter - Enhanced Edition")
        print("="*80)
        print("Features: Emoji categories, size hierarchy, visual connections")
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
            "LAYOUT": "📐"
        }
        print(f"[{timestamp}] {symbols.get(level, '•')} {message}")
    
    def sanitize_for_api(self, text: str) -> str:
        """Remove problematic Unicode characters while preserving emojis"""
        # Only replace truly problematic characters, keep emojis
        replacements = {
            '━': '─', '─': '-', '│': '|',
            '€': 'EUR', '™': 'TM', '®': '(R)',
            '"': '"', '"': '"', ''': "'", ''': "'"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove control characters but keep emojis (which are higher Unicode)
        text = ''.join(char for char in text if ord(char) >= 32 or ord(char) > 127000)
        return text
    
    def create_widget(self, text: str, x: int, y: int, 
                     size: WidgetSize = WidgetSize.STANDARD,
                     category: Optional[VisualCategory] = None) -> bool:
        """Create a widget with optional category emoji and custom size"""
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/sticky-note"
        
        # Add category emoji if specified
        if category:
            text = f"{category.value} {text}"
        
        width, height = size.value
        
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
                self.log(f"Created: '{text[:40]}...' at ({x}, {y})", "SUCCESS")
                return True
            else:
                self.log(f"Failed to create widget: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
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
    
    # ===== LAYOUT TEMPLATES =====
    
    def create_process_flow(self, steps: List[Dict], start_x: int = 100, start_y: int = 200):
        """
        Create a horizontal process flow with arrow connections
        
        steps = [
            {"text": "Step 1", "category": VisualCategory.START},
            {"text": "Step 2", "category": VisualCategory.PROCESS},
            ...
        ]
        """
        self.log("Creating Process Flow Layout", "LAYOUT")
        
        current_x = start_x
        current_y = start_y
        
        for i, step in enumerate(steps):
            # Create the main step widget
            category = step.get("category", VisualCategory.PROCESS)
            size = WidgetSize.SECTION if i == 0 else WidgetSize.STANDARD
            
            self.create_widget(
                step["text"],
                current_x,
                current_y,
                size=size,
                category=category
            )
            
            # Add arrow connector (except after last step)
            if i < len(steps) - 1:
                arrow_x = current_x + size.value[0] + 40
                arrow_y = current_y + (size.value[1] // 2) - 20
                self.create_arrow_connector(arrow_x, arrow_y, "→")
                current_x = arrow_x + WidgetSize.CONNECTOR.value[0] + 40
            
            time.sleep(0.2)
    
    def create_mind_map(self, center: str, branches: Dict[str, List[str]], 
                       start_x: int = 500, start_y: int = 400):
        """
        Create a mind map with central topic and radiating branches
        
        branches = {
            "north": ["Item 1", "Item 2"],
            "east": ["Item 3", "Item 4"],
            "south": ["Item 5", "Item 6"],
            "west": ["Item 7", "Item 8"]
        }
        """
        self.log("Creating Mind Map Layout", "LAYOUT")
        
        # Create central node
        self.create_widget(
            center,
            start_x,
            start_y,
            size=WidgetSize.HERO,
            category=VisualCategory.IDEA
        )
        
        # Branch positions and arrows
        positions = {
            "north": (start_x + 50, start_y - 200, "↑"),
            "east": (start_x + 400, start_y + 30, "→"),
            "south": (start_x + 50, start_y + 200, "↓"),
            "west": (start_x - 300, start_y + 30, "←")
        }
        
        for direction, items in branches.items():
            if direction in positions:
                branch_x, branch_y, arrow = positions[direction]
                
                # Add connector arrow
                if direction in ["north", "south"]:
                    arrow_x = start_x + 100
                    arrow_y = start_y - 80 if direction == "north" else start_y + 140
                else:
                    arrow_x = start_x + 220 if direction == "east" else start_x - 80
                    arrow_y = start_y + 40
                
                self.create_arrow_connector(arrow_x, arrow_y, arrow)
                
                # Add branch items
                for i, item in enumerate(items):
                    item_y = branch_y + (i * 120)
                    self.create_widget(
                        item,
                        branch_x,
                        item_y,
                        size=WidgetSize.COMPACT,
                        category=VisualCategory.INFO
                    )
                
                time.sleep(0.3)
    
    def create_kanban_board(self, columns: Dict[str, List[str]], 
                           start_x: int = 100, start_y: int = 150):
        """
        Create a Kanban-style board with columns
        
        columns = {
            "To Do": ["Task 1", "Task 2"],
            "In Progress": ["Task 3", "Task 4"],
            "Done": ["Task 5", "Task 6"]
        }
        """
        self.log("Creating Kanban Board Layout", "LAYOUT")
        
        column_categories = {
            "To Do": VisualCategory.QUESTION,
            "In Progress": VisualCategory.PROCESS,
            "Done": VisualCategory.COMPLETE,
            "Backlog": VisualCategory.TIME,
            "Review": VisualCategory.DOCUMENT
        }
        
        current_x = start_x
        
        for col_name, tasks in columns.items():
            # Column header
            category = column_categories.get(col_name, VisualCategory.INFO)
            self.create_widget(
                col_name,
                current_x,
                start_y,
                size=WidgetSize.SECTION,
                category=category
            )
            
            # Tasks in column
            task_y = start_y + 150
            for task in tasks:
                self.create_widget(
                    task,
                    current_x,
                    task_y,
                    size=WidgetSize.COMPACT,
                    category=None  # Use plain text for tasks
                )
                task_y += 120
            
            current_x += 300
            time.sleep(0.3)
    
    def create_decision_tree(self, question: str, branches: List[Dict],
                            start_x: int = 400, start_y: int = 150):
        """
        Create a decision tree with branching paths
        
        branches = [
            {
                "condition": "Yes",
                "outcome": "Action A",
                "sub_branches": [...]  # Optional nested branches
            },
            {
                "condition": "No",
                "outcome": "Action B"
            }
        ]
        """
        self.log("Creating Decision Tree Layout", "LAYOUT")
        
        # Main question
        self.create_widget(
            question,
            start_x,
            start_y,
            size=WidgetSize.SECTION,
            category=VisualCategory.QUESTION
        )
        
        # Branch arrows
        left_arrow_x = start_x - 50
        right_arrow_x = start_x + 200
        arrow_y = start_y + 120
        
        self.create_arrow_connector(left_arrow_x, arrow_y, "↙")
        self.create_arrow_connector(right_arrow_x, arrow_y, "↘")
        
        # Branches
        branch_y = start_y + 200
        branch_positions = [
            (start_x - 200, branch_y),  # Left branch
            (start_x + 250, branch_y)   # Right branch
        ]
        
        for i, branch in enumerate(branches[:2]):  # Limit to 2 main branches
            branch_x, branch_y = branch_positions[i]
            
            # Condition
            condition_category = VisualCategory.COMPLETE if branch["condition"] == "Yes" else VisualCategory.ERROR
            self.create_widget(
                branch["condition"],
                branch_x,
                branch_y,
                size=WidgetSize.ANNOTATION,
                category=condition_category
            )
            
            # Outcome
            self.create_widget(
                branch["outcome"],
                branch_x,
                branch_y + 100,
                size=WidgetSize.STANDARD,
                category=VisualCategory.GOAL
            )
            
            time.sleep(0.2)
    
    def create_network_diagram(self, nodes: List[Dict], connections: List[Tuple[int, int]],
                              start_x: int = 200, start_y: int = 200):
        """
        Create a network of interconnected nodes
        
        nodes = [
            {"text": "Node 1", "category": VisualCategory.START},
            {"text": "Node 2", "category": VisualCategory.PROCESS},
            ...
        ]
        connections = [(0, 1), (1, 2), ...]  # Index pairs
        """
        self.log("Creating Network Diagram", "LAYOUT")
        
        # Position nodes in a circular pattern
        import math
        num_nodes = len(nodes)
        radius = 200
        center_x = start_x + radius
        center_y = start_y + radius
        
        node_positions = []
        
        for i, node in enumerate(nodes):
            angle = (2 * math.pi * i) / num_nodes
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            node_positions.append((x, y))
            
            # Create node with number prefix
            numbered_text = f"{i+1}. {node['text']}"
            self.create_widget(
                numbered_text,
                int(x),
                int(y),
                size=WidgetSize.COMPACT,
                category=node.get("category", VisualCategory.INFO)
            )
        
        # Add connection indicators using small widgets
        for start_idx, end_idx in connections:
            if start_idx < len(node_positions) and end_idx < len(node_positions):
                start_x, start_y = node_positions[start_idx]
                end_x, end_y = node_positions[end_idx]
                
                # Place arrow widget at midpoint
                mid_x = int((start_x + end_x) / 2)
                mid_y = int((start_y + end_y) / 2)
                
                # Determine arrow direction
                if abs(end_x - start_x) > abs(end_y - start_y):
                    arrow = "→" if end_x > start_x else "←"
                else:
                    arrow = "↓" if end_y > start_y else "↑"
                
                self.create_arrow_connector(mid_x, mid_y, arrow)
            
            time.sleep(0.1)
    
    def demo_all_layouts(self):
        """Demonstrate all layout types with sample data"""
        self.log("\n🎨 Running Visual Formatter Demo", "VISUAL")
        
        # Clear board first
        self.clear_board()
        time.sleep(2)
        
        # 1. Process Flow (top left)
        self.log("\n1️⃣ Creating Process Flow", "VISUAL")
        process_steps = [
            {"text": "Start Process", "category": VisualCategory.START},
            {"text": "Validate Input", "category": VisualCategory.PROCESS},
            {"text": "Execute Task", "category": VisualCategory.PROCESS},
            {"text": "Review Results", "category": VisualCategory.WARNING},
            {"text": "Complete", "category": VisualCategory.COMPLETE}
        ]
        self.create_process_flow(process_steps, 100, 100)
        
        # 2. Mind Map (center)
        self.log("\n2️⃣ Creating Mind Map", "VISUAL")
        branches = {
            "north": ["Research", "Analysis"],
            "east": ["Development", "Testing"],
            "south": ["Documentation", "Training"],
            "west": ["Deployment", "Support"]
        }
        self.create_mind_map("Project Hub", branches, 600, 500)
        
        # 3. Kanban Board (bottom)
        self.log("\n3️⃣ Creating Kanban Board", "VISUAL")
        kanban_columns = {
            "To Do": ["Design UI", "Setup Database", "Create API"],
            "In Progress": ["User Auth", "Data Models"],
            "Done": ["Project Setup", "Requirements"]
        }
        self.create_kanban_board(kanban_columns, 100, 800)
        
        # 4. Decision Tree (right side)
        self.log("\n4️⃣ Creating Decision Tree", "VISUAL")
        decision_branches = [
            {"condition": "Yes", "outcome": "Implement Feature A"},
            {"condition": "No", "outcome": "Use Alternative B"}
        ]
        self.create_decision_tree("Should we use new framework?", decision_branches, 1200, 100)
        
        # 5. Small Network (bottom right)
        self.log("\n5️⃣ Creating Network Diagram", "VISUAL")
        network_nodes = [
            {"text": "Frontend", "category": VisualCategory.START},
            {"text": "API Gateway", "category": VisualCategory.PROCESS},
            {"text": "Backend", "category": VisualCategory.PROCESS},
            {"text": "Database", "category": VisualCategory.GOAL}
        ]
        connections = [(0, 1), (1, 2), (2, 3), (1, 3)]  # Frontend→API→Backend→DB, API→DB
        self.create_network_diagram(network_nodes, connections, 1100, 400)
        
        self.log("\n✅ Visual demonstration complete!", "SUCCESS")
        self.log(f"View your board: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}", "INFO")


def main():
    """Main execution with examples"""
    formatter = MuralVisualFormatter()
    
    print("\n" + "="*80)
    print("MURAL Visual Formatter - Interactive Demo")
    print("="*80)
    print("\nSelect a demo to run:")
    print("1. Full Demo (all layouts)")
    print("2. Process Flow only")
    print("3. Mind Map only")
    print("4. Kanban Board only")
    print("5. Decision Tree only")
    print("6. Network Diagram only")
    print("-"*80)
    
    # For automated testing, run full demo
    # In production, you'd get user input
    choice = "1"  # Default to full demo
    
    if choice == "1":
        formatter.demo_all_layouts()
    elif choice == "2":
        formatter.clear_board()
        steps = [
            {"text": "Receive Request", "category": VisualCategory.START},
            {"text": "Validate", "category": VisualCategory.PROCESS},
            {"text": "Process", "category": VisualCategory.PROCESS},
            {"text": "Complete", "category": VisualCategory.COMPLETE}
        ]
        formatter.create_process_flow(steps)
    elif choice == "3":
        formatter.clear_board()
        branches = {
            "north": ["Goal 1", "Goal 2"],
            "east": ["Task 1", "Task 2"],
            "south": ["Risk 1", "Risk 2"],
            "west": ["Resource 1", "Resource 2"]
        }
        formatter.create_mind_map("Central Idea", branches)
    elif choice == "4":
        formatter.clear_board()
        columns = {
            "Backlog": ["Feature 1", "Feature 2"],
            "To Do": ["Task A", "Task B"],
            "In Progress": ["Task C"],
            "Done": ["Task D", "Task E"]
        }
        formatter.create_kanban_board(columns)
    elif choice == "5":
        formatter.clear_board()
        branches = [
            {"condition": "Approve", "outcome": "Proceed with plan"},
            {"condition": "Reject", "outcome": "Revise proposal"}
        ]
        formatter.create_decision_tree("Budget > $10,000?", branches)
    elif choice == "6":
        formatter.clear_board()
        nodes = [
            {"text": "Server A", "category": VisualCategory.START},
            {"text": "Load Balancer", "category": VisualCategory.PROCESS},
            {"text": "Server B", "category": VisualCategory.PROCESS},
            {"text": "Database", "category": VisualCategory.GOAL},
            {"text": "Cache", "category": VisualCategory.INFO}
        ]
        connections = [(0, 1), (1, 2), (1, 3), (2, 3), (3, 4)]
        formatter.create_network_diagram(nodes, connections)


if __name__ == "__main__":
    main()
