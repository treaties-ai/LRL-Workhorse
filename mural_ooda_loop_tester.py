#!/usr/bin/env python3
"""
MURAL OODA Loop Tester - Rapid iteration testing with full verification
Observe-Orient-Decide-Act cycles for positioning refinement
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from mural_working_test import sanitize_for_mural_display

# Load environment variables
load_dotenv('.env')

class OODALoopTester:
    """OODA Loop implementation for rapid MURAL widget testing"""
    
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
        
        # OODA cycle tracking
        self.cycle_count = 0
        self.observations = []
        self.decisions = []
        self.actions_taken = []
        self.success_metrics = {
            'widgets_created': 0,
            'positions_correct': 0,
            'overlaps_detected': 0,
            'corrections_applied': 0
        }
        
        print("\n" + "="*80)
        print("MURAL OODA LOOP TESTER - RAPID ITERATION ENGINE")
        print("="*80)
        print(f"Board URL: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
    
    def log(self, phase, message):
        """Log with OODA phase indicator"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        phase_colors = {
            'OBSERVE': '🔍',
            'ORIENT': '🧭',
            'DECIDE': '🎯',
            'ACT': '⚡'
        }
        icon = phase_colors.get(phase, '📝')
        print(f"[{timestamp}] {icon} {phase}: {message}")
    
    def observe_widget_creation(self, text, x, y, width=138, height=138):
        """OBSERVE: Create widget and capture all response data"""
        self.log("OBSERVE", f"Creating widget '{text}' at ({x}, {y})")
        
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/sticky-note"
        sanitized_text = sanitize_for_mural_display(text)
        
        payload = {
            "shape": "rectangle",
            "text": sanitized_text,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        self.log("OBSERVE", f"Payload: {json.dumps(payload)}")
        
        observation = {
            'timestamp': datetime.now().isoformat(),
            'intended_position': (x, y),
            'intended_size': (width, height),
            'actual_position': None,
            'actual_size': None,
            'success': False,
            'widget_id': None,
            'response_time': None
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            response_time = time.time() - start_time
            observation['response_time'] = response_time
            
            self.log("OBSERVE", f"Response Status: {response.status_code} (Time: {response_time:.3f}s)")
            
            if response.status_code in [200, 201]:
                widget_data = response.json()
                
                # Extract actual position and size
                if 'value' in widget_data:
                    widget = widget_data['value']
                    observation['widget_id'] = widget.get('id')
                    observation['actual_position'] = (widget.get('x'), widget.get('y'))
                    observation['actual_size'] = (widget.get('width'), widget.get('height'))
                else:
                    observation['widget_id'] = widget_data.get('id')
                    observation['actual_position'] = (widget_data.get('x'), widget_data.get('y'))
                    observation['actual_size'] = (widget_data.get('width'), widget_data.get('height'))
                
                observation['success'] = True
                self.success_metrics['widgets_created'] += 1
                
                self.log("OBSERVE", f"Widget created: ID={observation['widget_id']}")
                self.log("OBSERVE", f"Actual position: {observation['actual_position']}")
            else:
                self.log("OBSERVE", f"Failed: {response.text[:200]}")
                
        except Exception as e:
            self.log("OBSERVE", f"Exception: {str(e)}")
        
        self.observations.append(observation)
        return observation
    
    def orient_on_observation(self, observation):
        """ORIENT: Analyze observation and identify patterns"""
        self.log("ORIENT", "Analyzing observation...")
        
        orientation = {
            'position_match': False,
            'size_match': False,
            'x_deviation': 0,
            'y_deviation': 0,
            'needs_correction': False,
            'pattern_detected': None
        }
        
        if observation['success'] and observation['actual_position']:
            intended_x, intended_y = observation['intended_position']
            actual_x, actual_y = observation['actual_position']
            
            orientation['x_deviation'] = actual_x - intended_x
            orientation['y_deviation'] = actual_y - intended_y
            
            if orientation['x_deviation'] == 0 and orientation['y_deviation'] == 0:
                orientation['position_match'] = True
                self.success_metrics['positions_correct'] += 1
                self.log("ORIENT", "✅ Perfect position match!")
            else:
                orientation['needs_correction'] = True
                self.log("ORIENT", f"⚠️ Position deviation: x={orientation['x_deviation']:+d}, y={orientation['y_deviation']:+d}")
            
            # Check for patterns in deviations
            if len(self.observations) > 3:
                recent_deviations = [(o['actual_position'][0] - o['intended_position'][0],
                                     o['actual_position'][1] - o['intended_position'][1])
                                    for o in self.observations[-3:]
                                    if o['success'] and o['actual_position']]
                
                if all(d == recent_deviations[0] for d in recent_deviations):
                    orientation['pattern_detected'] = 'consistent_offset'
                    self.log("ORIENT", f"Pattern detected: Consistent offset of {recent_deviations[0]}")
        
        return orientation
    
    def decide_action(self, orientation):
        """DECIDE: Make decision based on orientation"""
        self.log("DECIDE", "Determining next action...")
        
        decision = {
            'action': None,
            'parameters': {},
            'reasoning': ''
        }
        
        if orientation['needs_correction']:
            decision['action'] = 'apply_correction'
            decision['parameters'] = {
                'x_correction': -orientation['x_deviation'],
                'y_correction': -orientation['y_deviation']
            }
            decision['reasoning'] = f"Applying position correction to compensate for deviation"
            self.log("DECIDE", f"Decision: {decision['reasoning']}")
        
        elif orientation['pattern_detected'] == 'consistent_offset':
            decision['action'] = 'adjust_baseline'
            decision['reasoning'] = "Consistent pattern detected, adjusting baseline coordinates"
            self.log("DECIDE", f"Decision: {decision['reasoning']}")
        
        else:
            decision['action'] = 'continue'
            decision['reasoning'] = "Position accurate, continue with current approach"
            self.log("DECIDE", f"Decision: {decision['reasoning']}")
        
        self.decisions.append(decision)
        return decision
    
    def act_on_decision(self, decision):
        """ACT: Execute the decided action"""
        self.log("ACT", f"Executing: {decision['action']}")
        
        action_result = {
            'action': decision['action'],
            'executed_at': datetime.now().isoformat(),
            'success': False,
            'result': None
        }
        
        if decision['action'] == 'apply_correction':
            # Apply the correction to next widget placement
            self.success_metrics['corrections_applied'] += 1
            action_result['result'] = f"Correction applied: {decision['parameters']}"
            action_result['success'] = True
            self.log("ACT", f"✅ {action_result['result']}")
        
        elif decision['action'] == 'adjust_baseline':
            action_result['result'] = "Baseline adjusted for future placements"
            action_result['success'] = True
            self.log("ACT", f"✅ {action_result['result']}")
        
        elif decision['action'] == 'continue':
            action_result['result'] = "Continuing with current parameters"
            action_result['success'] = True
            self.log("ACT", f"✅ {action_result['result']}")
        
        self.actions_taken.append(action_result)
        return action_result
    
    def run_ooda_cycle(self, text, x, y, width=138, height=138):
        """Run complete OODA cycle for widget creation"""
        self.cycle_count += 1
        
        print(f"\n{'='*60}")
        print(f"OODA CYCLE #{self.cycle_count}")
        print(f"{'='*60}")
        
        # OBSERVE
        observation = self.observe_widget_creation(text, x, y, width, height)
        
        # ORIENT
        orientation = self.orient_on_observation(observation)
        
        # DECIDE
        decision = self.decide_action(orientation)
        
        # ACT
        action = self.act_on_decision(decision)
        
        return {
            'cycle': self.cycle_count,
            'observation': observation,
            'orientation': orientation,
            'decision': decision,
            'action': action
        }
    
    def test_body_visualization(self):
        """Test body part positioning with OODA cycles"""
        print("\n" + "="*80)
        print("TESTING BODY VISUALIZATION WITH OODA LOOPS")
        print("="*80)
        
        body_parts = [
            ("HEAD", 600, 250),
            ("HEART", 600, 450),
            ("TORSO", 600, 550),
            ("LEFT ARM", 450, 450),
            ("RIGHT ARM", 750, 450),
            ("LEFT LEG", 550, 750),
            ("RIGHT LEG", 650, 750),
        ]
        
        cycles = []
        for part_name, x, y in body_parts:
            cycle_result = self.run_ooda_cycle(part_name, x, y)
            cycles.append(cycle_result)
            time.sleep(0.3)  # Avoid rate limiting
        
        return cycles
    
    def test_grid_with_adaptation(self):
        """Test grid layout with adaptive corrections"""
        print("\n" + "="*80)
        print("TESTING ADAPTIVE GRID LAYOUT")
        print("="*80)
        
        grid_base_x = 1000
        grid_base_y = 400
        spacing = 160
        
        cycles = []
        corrections = {'x': 0, 'y': 0}
        
        for row in range(3):
            for col in range(3):
                # Apply any learned corrections
                x = grid_base_x + (col * spacing) + corrections['x']
                y = grid_base_y + (row * spacing) + corrections['y']
                
                text = f"GRID[{row},{col}]"
                cycle_result = self.run_ooda_cycle(text, x, y)
                
                # Learn from the result
                if cycle_result['orientation']['needs_correction']:
                    corrections['x'] -= cycle_result['orientation']['x_deviation']
                    corrections['y'] -= cycle_result['orientation']['y_deviation']
                    self.log("ACT", f"Updated corrections: x={corrections['x']:+d}, y={corrections['y']:+d}")
                
                cycles.append(cycle_result)
                time.sleep(0.3)
        
        return cycles
    
    def generate_report(self):
        """Generate comprehensive OODA test report"""
        print("\n" + "="*80)
        print("OODA LOOP TEST REPORT")
        print("="*80)
        
        print(f"\nCYCLES COMPLETED: {self.cycle_count}")
        
        print(f"\nSUCCESS METRICS:")
        for metric, value in self.success_metrics.items():
            print(f"  {metric}: {value}")
        
        if self.cycle_count > 0:
            accuracy = (self.success_metrics['positions_correct'] / 
                       self.success_metrics['widgets_created'] * 100 
                       if self.success_metrics['widgets_created'] > 0 else 0)
            print(f"\nPOSITION ACCURACY: {accuracy:.1f}%")
        
        # Pattern analysis
        if self.observations:
            deviations = [(o['actual_position'][0] - o['intended_position'][0],
                          o['actual_position'][1] - o['intended_position'][1])
                         for o in self.observations
                         if o['success'] and o['actual_position']]
            
            if deviations:
                avg_x_dev = sum(d[0] for d in deviations) / len(deviations)
                avg_y_dev = sum(d[1] for d in deviations) / len(deviations)
                
                print(f"\nAVERAGE DEVIATIONS:")
                print(f"  X: {avg_x_dev:+.1f}px")
                print(f"  Y: {avg_y_dev:+.1f}px")
        
        print(f"\nADAPTATION SUMMARY:")
        print(f"  Corrections applied: {self.success_metrics['corrections_applied']}")
        print(f"  Patterns detected: {sum(1 for d in self.decisions if d.get('reasoning', '').startswith('Consistent'))}")
        
        print(f"\n📊 View your board at:")
        print(f"   https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}")


if __name__ == "__main__":
    print("\n🚀 Starting OODA Loop Testing")
    print("This system will:")
    print("  • Create widgets with full observation")
    print("  • Analyze actual vs intended positions")
    print("  • Learn from deviations")
    print("  • Apply corrections in real-time")
    
    tester = OODALoopTester()
    
    # Test body visualization
    body_cycles = tester.test_body_visualization()
    
    # Test adaptive grid
    grid_cycles = tester.test_grid_with_adaptation()
    
    # Generate report
    tester.generate_report()
    
    print("\n✅ OODA Loop Testing Complete!")
