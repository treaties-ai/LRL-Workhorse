#!/usr/bin/env python3
"""
MURAL Layout Engine - Calculates optimal positions for widgets
Provides anatomical positioning, ring layouts, and grid systems
"""

import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class Position:
    """Represents a position on the MURAL board"""
    x: int
    y: int
    
    def offset(self, dx: int, dy: int) -> 'Position':
        """Return a new position offset by dx, dy"""
        return Position(self.x + dx, self.y + dy)

class MuralLayoutEngine:
    """Manages widget positioning with various layout algorithms"""
    
    # Board dimensions (typical MURAL board space)
    BOARD_WIDTH = 2000
    BOARD_HEIGHT = 2000
    
    # Layout zones
    ZONES = {
        "body": Position(600, 400),      # Center-left for body visualization
        "categories": Position(1200, 400), # Center-right for categories
        "legend": Position(50, 50),       # Top-left for legend
        "header": Position(1000, 50),     # Top-center for headers
        "tdai": Position(1600, 400),      # Right side for TDAI scores
    }
    
    # Anatomical positions for body parts
    BODY_POSITIONS = {
        "HEAD": Position(600, 250),
        "NECK": Position(600, 320),
        "SHOULDERS": Position(600, 370),
        "HEART": Position(600, 450),
        "CHEST": Position(600, 430),
        "TORSO": Position(600, 550),
        "STOMACH": Position(600, 580),
        "LEFT_ARM": Position(450, 450),
        "RIGHT_ARM": Position(750, 450),
        "LEFT_HAND": Position(380, 550),
        "RIGHT_HAND": Position(820, 550),
        "HIPS": Position(600, 650),
        "LEFT_LEG": Position(550, 750),
        "RIGHT_LEG": Position(650, 750),
        "LEFT_FOOT": Position(530, 850),
        "RIGHT_FOOT": Position(670, 850),
    }
    
    def __init__(self):
        """Initialize the layout engine"""
        self.widget_positions = []  # Track used positions to avoid overlap
        self.grid_index = 0  # For grid layout tracking
        
    def get_anatomical_position(self, body_part: str) -> Position:
        """
        Get the anatomical position for a body part
        
        Args:
            body_part: Name of the body part (e.g., "HEAD", "HEART")
            
        Returns:
            Position object for the body part
        """
        # Check for exact match
        part_upper = body_part.upper()
        if part_upper in self.BODY_POSITIONS:
            return self.BODY_POSITIONS[part_upper]
        
        # Check for partial matches
        for key, pos in self.BODY_POSITIONS.items():
            if key in part_upper or part_upper in key:
                return pos
        
        # Default to torso area if not found
        return self.BODY_POSITIONS["TORSO"]
    
    def calculate_ring_positions(self, items: List[str], center: Position, 
                                radius: int = 200) -> List[Position]:
        """
        Calculate positions for items arranged in a ring
        
        Args:
            items: List of items to position
            center: Center position of the ring
            radius: Radius of the ring
            
        Returns:
            List of Position objects
        """
        positions = []
        num_items = len(items)
        
        if num_items == 0:
            return positions
        
        # Calculate angle step between items
        angle_step = 2 * math.pi / num_items
        
        for i in range(num_items):
            angle = i * angle_step - math.pi / 2  # Start from top
            x = int(center.x + radius * math.cos(angle))
            y = int(center.y + radius * math.sin(angle))
            positions.append(Position(x, y))
        
        return positions
    
    def calculate_grid_positions(self, num_items: int, start: Position,
                                cols: int = 4, spacing_x: int = 180,
                                spacing_y: int = 180) -> List[Position]:
        """
        Calculate positions for items in a grid layout
        
        Args:
            num_items: Number of items to position
            start: Starting position for the grid
            cols: Number of columns
            spacing_x: Horizontal spacing between items
            spacing_y: Vertical spacing between items
            
        Returns:
            List of Position objects
        """
        positions = []
        
        for i in range(num_items):
            row = i // cols
            col = i % cols
            x = start.x + (col * spacing_x)
            y = start.y + (row * spacing_y)
            positions.append(Position(x, y))
        
        return positions
    
    def calculate_cluster_positions(self, main_item: str, related_items: List[str],
                                   center: Position, cluster_radius: int = 100) -> Dict[str, Position]:
        """
        Calculate positions for a main item with related items clustered around it
        
        Args:
            main_item: The central item
            related_items: Items to cluster around the main item
            center: Center position for the main item
            cluster_radius: Distance of related items from center
            
        Returns:
            Dictionary mapping item names to positions
        """
        positions = {main_item: center}
        
        # Position related items in a circle around the main item
        if related_items:
            ring_positions = self.calculate_ring_positions(
                related_items, center, cluster_radius
            )
            for item, pos in zip(related_items, ring_positions):
                positions[item] = pos
        
        return positions
    
    def get_zone_position(self, zone: str, offset_x: int = 0, offset_y: int = 0) -> Position:
        """
        Get a position within a predefined zone
        
        Args:
            zone: Zone name (e.g., "body", "categories", "legend")
            offset_x: X offset from zone center
            offset_y: Y offset from zone center
            
        Returns:
            Position object
        """
        if zone in self.ZONES:
            base_pos = self.ZONES[zone]
            return Position(base_pos.x + offset_x, base_pos.y + offset_y)
        return Position(500, 500)  # Default center position
    
    def calculate_tdai_positions(self, tdai_scores: List[Tuple[str, float]]) -> List[Position]:
        """
        Calculate positions for TDAI scores, arranged by severity
        
        Args:
            tdai_scores: List of (text, score) tuples
            
        Returns:
            List of Position objects
        """
        # Sort by score (highest first)
        sorted_scores = sorted(tdai_scores, key=lambda x: x[1], reverse=True)
        
        # Position in TDAI zone, stacked vertically
        positions = []
        tdai_zone = self.ZONES["tdai"]
        
        for i, (text, score) in enumerate(sorted_scores):
            y_offset = i * 160  # Vertical spacing
            positions.append(Position(tdai_zone.x, tdai_zone.y + y_offset))
        
        return positions
    
    def avoid_overlap(self, position: Position, min_distance: int = 150) -> Position:
        """
        Adjust position to avoid overlap with existing widgets
        
        Args:
            position: Desired position
            min_distance: Minimum distance from other widgets
            
        Returns:
            Adjusted position
        """
        for existing_pos in self.widget_positions:
            distance = math.sqrt(
                (position.x - existing_pos.x) ** 2 + 
                (position.y - existing_pos.y) ** 2
            )
            
            if distance < min_distance:
                # Adjust position to avoid overlap
                angle = math.atan2(
                    position.y - existing_pos.y,
                    position.x - existing_pos.x
                )
                new_x = int(existing_pos.x + min_distance * math.cos(angle))
                new_y = int(existing_pos.y + min_distance * math.sin(angle))
                position = Position(new_x, new_y)
        
        # Track this position
        self.widget_positions.append(position)
        return position
    
    def create_body_visualization_layout(self) -> Dict[str, Position]:
        """
        Create a complete body visualization layout
        
        Returns:
            Dictionary mapping body part names to positions
        """
        layout = {}
        
        # Add all body parts with slight randomization for organic feel
        import random
        for part, base_pos in self.BODY_POSITIONS.items():
            # Add small random offset for organic layout
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            layout[part] = Position(
                base_pos.x + offset_x,
                base_pos.y + offset_y
            )
        
        return layout
    
    def calculate_category_layout(self, categories: Dict[str, List[str]]) -> Dict[str, Position]:
        """
        Calculate layout for categorized items
        
        Args:
            categories: Dictionary mapping category names to item lists
            
        Returns:
            Dictionary mapping all items to positions
        """
        all_positions = {}
        
        # Start position for categories
        cat_start = self.ZONES["categories"]
        cat_y = cat_start.y
        
        for category, items in categories.items():
            # Category header position
            all_positions[category] = Position(cat_start.x, cat_y)
            
            # Items in this category (grid layout)
            item_positions = self.calculate_grid_positions(
                len(items),
                Position(cat_start.x + 50, cat_y + 60),
                cols=3,
                spacing_x=160,
                spacing_y=140
            )
            
            for item, pos in zip(items, item_positions):
                all_positions[item] = pos
            
            # Move to next category area
            rows_needed = (len(items) + 2) // 3  # 3 columns
            cat_y += 60 + (rows_needed * 140) + 40  # Header + items + spacing
        
        return all_positions
    
    def get_optimal_position(self, content_type: str, text: str, 
                            index: int = 0) -> Position:
        """
        Get the optimal position for a widget based on its content
        
        Args:
            content_type: Type of content (e.g., "BODY_PART", "TDAI", "CATEGORY")
            text: The widget text
            index: Index for grid/list positioning
            
        Returns:
            Optimal Position object
        """
        # Check if it's a body part
        if content_type == "BODY_PART" or any(part in text.upper() for part in self.BODY_POSITIONS.keys()):
            for part in self.BODY_POSITIONS.keys():
                if part in text.upper():
                    return self.get_anatomical_position(part)
        
        # Check for TDAI scores
        if content_type == "TDAI" or "TDAI" in text.upper():
            tdai_zone = self.ZONES["tdai"]
            return Position(tdai_zone.x, tdai_zone.y + (index * 160))
        
        # Check for categories
        if content_type in ["THREAT", "COMPANY", "EMOTION", "GROUNDING"]:
            cat_zone = self.ZONES["categories"]
            return Position(cat_zone.x, cat_zone.y + (index * 160))
        
        # Default to grid layout
        grid_start = Position(1000, 600)
        positions = self.calculate_grid_positions(index + 1, grid_start)
        return positions[-1] if positions else grid_start


# Test function for standalone execution
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MURAL LAYOUT ENGINE TEST")
    print("="*70)
    
    engine = MuralLayoutEngine()
    
    print("\n1. Testing anatomical positions:")
    body_parts = ["HEAD", "HEART", "LEFT_ARM", "RIGHT_LEG"]
    for part in body_parts:
        pos = engine.get_anatomical_position(part)
        print(f"   {part}: ({pos.x}, {pos.y})")
    
    print("\n2. Testing ring layout:")
    items = ["Item1", "Item2", "Item3", "Item4"]
    center = Position(800, 400)
    ring_positions = engine.calculate_ring_positions(items, center, 150)
    for item, pos in zip(items, ring_positions):
        print(f"   {item}: ({pos.x}, {pos.y})")
    
    print("\n3. Testing grid layout:")
    grid_positions = engine.calculate_grid_positions(6, Position(100, 100))
    for i, pos in enumerate(grid_positions):
        print(f"   Widget {i+1}: ({pos.x}, {pos.y})")
    
    print("\n4. Testing category layout:")
    categories = {
        "THREATS": ["Threat1", "Threat2", "Threat3"],
        "EMOTIONS": ["Grief", "Anger", "Fear", "Sadness"],
    }
    cat_layout = engine.calculate_category_layout(categories)
    for item, pos in cat_layout.items():
        print(f"   {item}: ({pos.x}, {pos.y})")
    
    print("\n✅ Layout engine test complete!")
