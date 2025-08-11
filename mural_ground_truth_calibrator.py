#!/usr/bin/env python3
"""
MURAL Ground Truth Calibrator - Establish verified baseline for widget positioning
This creates single widgets with FULL logging and verification at every step
No assumptions, only verified facts.
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class GroundTruthCalibrator:
    """Establishes ground truth for MURAL widget positioning with full verification"""
    
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
        
        # Track all test results
        self.test_results = []
        self.position_deviations = []
        
        print("\n" + "="*80)
        print("MURAL GROUND TRUTH CALIBRATOR - VERIFICATION-FIRST APPROACH")
        print("="*80)
        print(f"Board URL: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
    
    def log_operation(self, operation, details):
        """Log every operation with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {operation}: {details}")
    
    def create_widget_with_verification(self, text, x, y, width=138, height=138):
        """Create a widget with FULL logging and verification"""
        
        self.log_operation("INTENT", f"Create widget '{text}' at x={x}, y={y}, w={width}, h={height}")
        
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/sticky-note"
        
        payload = {
            "shape": "rectangle",
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        self.log_operation("API_CALL", f"POST {endpoint}")
        self.log_operation("PAYLOAD", json.dumps(payload))
        
        try:
            # Make the API call
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            
            self.log_operation("RESPONSE_STATUS", f"{response.status_code}")
            
            if response.status_code in [200, 201]:
                # Parse response to get actual widget data
                widget_data = response.json()
                
                # Extract widget ID and actual position
                widget_id = None
                actual_x = None
                actual_y = None
                actual_width = None
                actual_height = None
                
                # Handle different response structures
                if 'value' in widget_data:
                    widget = widget_data['value']
                    widget_id = widget.get('id', 'unknown')
                    actual_x = widget.get('x')
                    actual_y = widget.get('y')
                    actual_width = widget.get('width')
                    actual_height = widget.get('height')
                elif 'id' in widget_data:
                    widget_id = widget_data['id']
                    actual_x = widget_data.get('x')
                    actual_y = widget_data.get('y')
                    actual_width = widget_data.get('width')
                    actual_height = widget_data.get('height')
                
                self.log_operation("WIDGET_ID", widget_id)
                
                # Verify position
                if actual_x is not None and actual_y is not None:
                    self.log_operation("ACTUAL_POSITION", f"x={actual_x}, y={actual_y}")
                    self.log_operation("ACTUAL_SIZE", f"w={actual_width}, h={actual_height}")
                    
                    # Calculate deviations
                    x_deviation = actual_x - x
                    y_deviation = actual_y - y
                    width_deviation = actual_width - width if actual_width else 0
                    height_deviation = actual_height - height if actual_height else 0
                    
                    self.log_operation("POSITION_DEVIATION", f"x_offset={x_deviation:+d}, y_offset={y_deviation:+d}")
                    self.log_operation("SIZE_DEVIATION", f"w_offset={width_deviation:+d}, h_offset={height_deviation:+d}")
                    
                    # Store results
                    result = {
                        'widget_id': widget_id,
                        'text': text,
                        'intended_position': (x, y),
                        'actual_position': (actual_x, actual_y),
                        'intended_size': (width, height),
                        'actual_size': (actual_width, actual_height),
                        'position_deviation': (x_deviation, y_deviation),
                        'size_deviation': (width_deviation, height_deviation)
                    }
                    
                    self.test_results.append(result)
                    self.position_deviations.append((x_deviation, y_deviation))
                    
                    # Verification status
                    if x_deviation == 0 and y_deviation == 0:
                        self.log_operation("VERIFICATION", "✅ PERFECT MATCH - Position exact!")
                    else:
                        self.log_operation("VERIFICATION", f"⚠️ POSITION MISMATCH - Offset detected")
                    
                    return result
                else:
                    self.log_operation("ERROR", "Position data not found in response")
                    self.log_operation("RAW_RESPONSE", json.dumps(widget_data)[:500])
                    return None
            else:
                self.log_operation("ERROR", f"API returned {response.status_code}")
                self.log_operation("ERROR_DETAILS", response.text[:300])
                return None
                
        except Exception as e:
            self.log_operation("EXCEPTION", str(e))
            return None
    
    def test_single_widget(self):
        """Test 1: Single widget at known position"""
        print("\n" + "="*60)
        print("TEST 1: SINGLE WIDGET GROUND TRUTH")
        print("="*60)
        
        result = self.create_widget_with_verification(
            "GROUND TRUTH TEST",
            x=100,
            y=100,
            width=138,
            height=138
        )
        
        if result:
            print("\n✅ Test 1 Complete - Ground truth established")
        else:
            print("\n❌ Test 1 Failed - Check logs above")
        
        return result
    
    def test_horizontal_spacing(self):
        """Test 2: Horizontal spacing calibration"""
        print("\n" + "="*60)
        print("TEST 2: HORIZONTAL SPACING CALIBRATION")
        print("="*60)
        
        x_positions = [100, 300, 500, 700, 900]
        y_position = 300
        
        results = []
        for i, x in enumerate(x_positions):
            self.log_operation("TEST", f"Widget {i+1}/5 at x={x}")
            result = self.create_widget_with_verification(
                f"H-TEST-{i+1}",
                x=x,
                y=y_position,
                width=138,
                height=138
            )
            results.append(result)
            time.sleep(0.3)  # Avoid rate limiting
        
        # Analyze spacing
        print("\n" + "-"*40)
        print("HORIZONTAL SPACING ANALYSIS:")
        actual_positions = [r['actual_position'][0] for r in results if r]
        
        if len(actual_positions) > 1:
            spacings = []
            for i in range(1, len(actual_positions)):
                spacing = actual_positions[i] - actual_positions[i-1]
                spacings.append(spacing)
                print(f"  Spacing {i}: {spacing}px (expected: 200px, deviation: {spacing-200:+d}px)")
            
            avg_spacing = sum(spacings) / len(spacings)
            print(f"\n  Average spacing: {avg_spacing:.1f}px")
            print(f"  Spacing consistency: {'✅ GOOD' if all(180 <= s <= 220 for s in spacings) else '⚠️ INCONSISTENT'}")
        
        return results
    
    def test_vertical_spacing(self):
        """Test 3: Vertical spacing calibration"""
        print("\n" + "="*60)
        print("TEST 3: VERTICAL SPACING CALIBRATION")
        print("="*60)
        
        x_position = 1200
        y_positions = [100, 300, 500, 700, 900]
        
        results = []
        for i, y in enumerate(y_positions):
            self.log_operation("TEST", f"Widget {i+1}/5 at y={y}")
            result = self.create_widget_with_verification(
                f"V-TEST-{i+1}",
                x=x_position,
                y=y,
                width=138,
                height=138
            )
            results.append(result)
            time.sleep(0.3)
        
        # Analyze spacing
        print("\n" + "-"*40)
        print("VERTICAL SPACING ANALYSIS:")
        actual_positions = [r['actual_position'][1] for r in results if r]
        
        if len(actual_positions) > 1:
            spacings = []
            for i in range(1, len(actual_positions)):
                spacing = actual_positions[i] - actual_positions[i-1]
                spacings.append(spacing)
                print(f"  Spacing {i}: {spacing}px (expected: 200px, deviation: {spacing-200:+d}px)")
            
            avg_spacing = sum(spacings) / len(spacings)
            print(f"\n  Average spacing: {avg_spacing:.1f}px")
            print(f"  Spacing consistency: {'✅ GOOD' if all(180 <= s <= 220 for s in spacings) else '⚠️ INCONSISTENT'}")
        
        return results
    
    def test_grid_layout(self):
        """Test 4: 3x3 grid verification"""
        print("\n" + "="*60)
        print("TEST 4: 3x3 GRID LAYOUT VERIFICATION")
        print("="*60)
        
        grid_start_x = 600
        grid_start_y = 600
        spacing = 160
        
        results = []
        for row in range(3):
            for col in range(3):
                x = grid_start_x + (col * spacing)
                y = grid_start_y + (row * spacing)
                
                self.log_operation("TEST", f"Grid [{row},{col}] at ({x}, {y})")
                result = self.create_widget_with_verification(
                    f"G[{row},{col}]",
                    x=x,
                    y=y,
                    width=138,
                    height=138
                )
                results.append(result)
                time.sleep(0.3)
        
        # Analyze grid alignment
        print("\n" + "-"*40)
        print("GRID ALIGNMENT ANALYSIS:")
        
        if results:
            # Check row alignment
            for row in range(3):
                row_widgets = results[row*3:(row+1)*3]
                y_positions = [w['actual_position'][1] for w in row_widgets if w]
                if y_positions:
                    y_variance = max(y_positions) - min(y_positions)
                    print(f"  Row {row} Y-variance: {y_variance}px {'✅' if y_variance <= 5 else '⚠️'}")
            
            # Check column alignment
            for col in range(3):
                col_widgets = [results[row*3 + col] for row in range(3)]
                x_positions = [w['actual_position'][0] for w in col_widgets if w]
                if x_positions:
                    x_variance = max(x_positions) - min(x_positions)
                    print(f"  Col {col} X-variance: {x_variance}px {'✅' if x_variance <= 5 else '⚠️'}")
        
        return results
    
    def generate_correction_matrix(self):
        """Generate correction factors from all test results"""
        print("\n" + "="*60)
        print("CORRECTION MATRIX GENERATION")
        print("="*60)
        
        if not self.position_deviations:
            print("No deviation data collected")
            return None
        
        # Calculate average deviations
        x_deviations = [d[0] for d in self.position_deviations]
        y_deviations = [d[1] for d in self.position_deviations]
        
        avg_x_deviation = sum(x_deviations) / len(x_deviations)
        avg_y_deviation = sum(y_deviations) / len(y_deviations)
        
        max_x_deviation = max(abs(x) for x in x_deviations)
        max_y_deviation = max(abs(y) for y in y_deviations)
        
        print(f"\nDEVIATION STATISTICS:")
        print(f"  Average X deviation: {avg_x_deviation:+.1f}px")
        print(f"  Average Y deviation: {avg_y_deviation:+.1f}px")
        print(f"  Max X deviation: {max_x_deviation}px")
        print(f"  Max Y deviation: {max_y_deviation}px")
        
        # Generate correction matrix
        correction_matrix = {
            'x_offset': -avg_x_deviation,  # Negate to correct
            'y_offset': -avg_y_deviation,
            'confidence': 'HIGH' if max_x_deviation <= 10 and max_y_deviation <= 10 else 'MEDIUM'
        }
        
        print(f"\nCORRECTION MATRIX:")
        print(f"  Apply X correction: {correction_matrix['x_offset']:+.1f}px")
        print(f"  Apply Y correction: {correction_matrix['y_offset']:+.1f}px")
        print(f"  Confidence level: {correction_matrix['confidence']}")
        
        return correction_matrix
    
    def run_full_calibration(self):
        """Run complete calibration suite"""
        print("\n" + "="*80)
        print("STARTING FULL CALIBRATION SUITE")
        print("="*80)
        
        # Run all tests
        self.test_single_widget()
        time.sleep(1)
        
        self.test_horizontal_spacing()
        time.sleep(1)
        
        self.test_vertical_spacing()
        time.sleep(1)
        
        self.test_grid_layout()
        
        # Generate correction matrix
        correction_matrix = self.generate_correction_matrix()
        
        # Final summary
        print("\n" + "="*80)
        print("CALIBRATION COMPLETE")
        print("="*80)
        
        total_widgets = len(self.test_results)
        perfect_matches = sum(1 for r in self.test_results if r['position_deviation'] == (0, 0))
        
        print(f"\nSUMMARY:")
        print(f"  Total widgets created: {total_widgets}")
        print(f"  Perfect position matches: {perfect_matches}/{total_widgets}")
        if total_widgets > 0:
            print(f"  Position accuracy: {perfect_matches/total_widgets*100:.1f}%")
        else:
            print(f"  Position accuracy: N/A (no widgets created)")
        
        if correction_matrix:
            print(f"\nRECOMMENDED CORRECTIONS:")
            print(f"  Add {correction_matrix['x_offset']:+.1f}px to all X coordinates")
            print(f"  Add {correction_matrix['y_offset']:+.1f}px to all Y coordinates")
        
        print(f"\n📊 View results at:")
        print(f"   https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}")
        
        return correction_matrix


if __name__ == "__main__":
    calibrator = GroundTruthCalibrator()
    correction_matrix = calibrator.run_full_calibration()
    
    # Save correction matrix for use by other scripts
    if correction_matrix:
        with open('mural_correction_matrix.json', 'w') as f:
            json.dump(correction_matrix, f, indent=2)
        print(f"\n✅ Correction matrix saved to mural_correction_matrix.json")
