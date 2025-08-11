#!/usr/bin/env python3
"""
Spacing Quality Assurance Tests for MURAL Visual Formatter
Ensures no overlapping and proper spacing between all widgets
"""

import time
from mural_visual_formatter_v2 import (
    MuralVisualFormatterV2, 
    VisualCategory, 
    WidgetSize,
    LayoutZone,
    WidgetBounds
)

class SpacingQualityTester:
    """Test suite for spacing and collision detection"""
    
    def __init__(self):
        self.formatter = MuralVisualFormatterV2()
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        result = "✅ PASSED" if passed else "❌ FAILED"
        print(f"\n[TEST] {test_name}: {result}")
        if details:
            print(f"       Details: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_single_widget_placement(self):
        """Test that a single widget can be placed"""
        print("\n" + "="*60)
        print("TEST 1: Single Widget Placement")
        print("="*60)
        
        self.formatter.clear_board()
        
        # Place a single widget
        success = self.formatter.create_widget(
            "Test Widget",
            100, 100,
            size=WidgetSize.STANDARD,
            category=VisualCategory.INFO
        )
        
        # Check if widget was registered
        widget_count = len(self.formatter.registry.widgets)
        self.log_test(
            "Single Widget Placement",
            success and widget_count == 1,
            f"Widget created: {success}, Registry count: {widget_count}"
        )
    
    def test_collision_detection(self):
        """Test that overlapping widgets are detected and repositioned"""
        print("\n" + "="*60)
        print("TEST 2: Collision Detection")
        print("="*60)
        
        self.formatter.clear_board()
        
        # Place first widget
        self.formatter.create_widget(
            "Widget 1",
            200, 200,
            size=WidgetSize.STANDARD
        )
        
        # Try to place overlapping widget (should be repositioned)
        self.formatter.create_widget(
            "Widget 2",
            210, 210,  # Overlapping position
            size=WidgetSize.STANDARD
        )
        
        # Check that widgets don't overlap
        if len(self.formatter.registry.widgets) >= 2:
            widget1 = self.formatter.registry.widgets[0]
            widget2 = self.formatter.registry.widgets[1]
            
            # They should not overlap
            overlaps = widget1.overlaps_with(widget2, buffer=20)
            
            self.log_test(
                "Collision Detection",
                not overlaps,
                f"Widget 1: ({widget1.x}, {widget1.y}), Widget 2: ({widget2.x}, {widget2.y})"
            )
        else:
            self.log_test(
                "Collision Detection",
                False,
                "Not enough widgets created"
            )
    
    def test_minimum_spacing(self):
        """Test that minimum spacing is maintained between widgets"""
        print("\n" + "="*60)
        print("TEST 3: Minimum Spacing Enforcement")
        print("="*60)
        
        self.formatter.clear_board()
        
        # Place a grid of widgets
        positions = [
            (100, 100), (300, 100), (500, 100),
            (100, 300), (300, 300), (500, 300)
        ]
        
        for i, (x, y) in enumerate(positions):
            self.formatter.create_widget(
                f"Grid {i+1}",
                x, y,
                size=WidgetSize.COMPACT
            )
        
        # Check minimum spacing between all widgets
        min_distance = float('inf')
        for i, widget1 in enumerate(self.formatter.registry.widgets):
            for j, widget2 in enumerate(self.formatter.registry.widgets):
                if i != j:
                    # Calculate edge-to-edge distance
                    h_dist = max(0, max(widget1.left, widget2.left) - 
                                min(widget1.right, widget2.right))
                    v_dist = max(0, max(widget1.top, widget2.top) - 
                                min(widget1.bottom, widget2.bottom))
                    
                    if h_dist > 0 or v_dist > 0:
                        distance = max(h_dist, v_dist)
                        min_distance = min(min_distance, distance)
        
        # Should maintain at least 20 pixels spacing
        self.log_test(
            "Minimum Spacing",
            min_distance >= 20,
            f"Minimum distance found: {min_distance} pixels"
        )
    
    def test_zone_boundaries(self):
        """Test that layouts stay within their designated zones"""
        print("\n" + "="*60)
        print("TEST 4: Zone Boundary Enforcement")
        print("="*60)
        
        self.formatter.clear_board()
        
        # Create a process flow in its zone
        steps = [
            {"text": "Step 1", "category": VisualCategory.START},
            {"text": "Step 2", "category": VisualCategory.PROCESS}
        ]
        self.formatter.create_process_flow(steps, LayoutZone.PROCESS_FLOW)
        
        # Check all widgets are within the zone
        zone_bounds = LayoutZone.PROCESS_FLOW.value
        x_min, y_min, x_max, y_max = zone_bounds
        
        widgets_in_zone = True
        for widget in self.formatter.registry.widgets:
            if not (x_min <= widget.x <= x_max and 
                   y_min <= widget.y <= y_max and
                   widget.right <= x_max and 
                   widget.bottom <= y_max):
                widgets_in_zone = False
                break
        
        self.log_test(
            "Zone Boundaries",
            widgets_in_zone,
            f"All widgets within zone: {widgets_in_zone}"
        )
    
    def test_arrow_alignment(self):
        """Test that arrow connectors are properly positioned"""
        print("\n" + "="*60)
        print("TEST 5: Arrow Connector Alignment")
        print("="*60)
        
        self.formatter.clear_board()
        
        # Create simple process flow
        steps = [
            {"text": "Start", "category": VisualCategory.START},
            {"text": "End", "category": VisualCategory.COMPLETE}
        ]
        self.formatter.create_process_flow(steps)
        
        # Find arrow widgets (they have small width)
        arrows = [w for w in self.formatter.registry.widgets 
                 if w.width == WidgetSize.CONNECTOR.value[0]]
        
        # Check arrow is between main widgets
        if len(arrows) > 0 and len(self.formatter.registry.widgets) >= 3:
            arrow = arrows[0]
            widgets = [w for w in self.formatter.registry.widgets 
                      if w.width != WidgetSize.CONNECTOR.value[0]]
            
            if len(widgets) >= 2:
                widget1 = widgets[0]
                widget2 = widgets[1]
                
                # Arrow should be between the two widgets
                arrow_between = (widget1.right < arrow.x < widget2.left)
                
                self.log_test(
                    "Arrow Alignment",
                    arrow_between,
                    f"Arrow at x={arrow.x} between widgets at x={widget1.right} and x={widget2.left}"
                )
            else:
                self.log_test("Arrow Alignment", False, "Not enough main widgets")
        else:
            self.log_test("Arrow Alignment", False, "No arrow connectors found")
    
    def test_progressive_complexity(self):
        """Test with progressively more complex layouts"""
        print("\n" + "="*60)
        print("TEST 6: Progressive Complexity")
        print("="*60)
        
        test_cases = [
            ("2 widgets", 2),
            ("5 widgets", 5),
            ("10 widgets", 10),
            ("20 widgets", 20)
        ]
        
        for test_name, count in test_cases:
            self.formatter.clear_board()
            
            # Create widgets in a spiral pattern
            import math
            center_x, center_y = 500, 500
            
            for i in range(count):
                angle = (2 * math.pi * i) / count
                radius = 100 + (i * 20)
                x = int(center_x + radius * math.cos(angle))
                y = int(center_y + radius * math.sin(angle))
                
                self.formatter.create_widget(
                    f"Widget {i+1}",
                    x, y,
                    size=WidgetSize.COMPACT
                )
            
            # Check no overlaps
            has_overlap = False
            for i, widget1 in enumerate(self.formatter.registry.widgets):
                for j, widget2 in enumerate(self.formatter.registry.widgets):
                    if i < j and widget1.overlaps_with(widget2, buffer=10):
                        has_overlap = True
                        break
                if has_overlap:
                    break
            
            self.log_test(
                f"Progressive - {test_name}",
                not has_overlap,
                f"Created {len(self.formatter.registry.widgets)} widgets, overlaps: {has_overlap}"
            )
    
    def run_all_tests(self):
        """Run all spacing quality tests"""
        print("\n" + "="*80)
        print("🔍 SPACING QUALITY ASSURANCE TEST SUITE")
        print("="*80)
        
        # Run each test
        self.test_single_widget_placement()
        time.sleep(1)
        
        self.test_collision_detection()
        time.sleep(1)
        
        self.test_minimum_spacing()
        time.sleep(1)
        
        self.test_zone_boundaries()
        time.sleep(1)
        
        self.test_arrow_alignment()
        time.sleep(1)
        
        self.test_progressive_complexity()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        print(f"\nTests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Spacing quality assured.")
        else:
            print("⚠️ Some tests failed. Review spacing implementation.")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed == total


def main():
    """Run the spacing quality tests"""
    tester = SpacingQualityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Ready to create properly spaced MURAL boards!")
    else:
        print("\n❌ Spacing issues detected. Please review the implementation.")


if __name__ == "__main__":
    main()
