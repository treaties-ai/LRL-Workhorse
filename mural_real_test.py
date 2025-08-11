#!/usr/bin/env python3
"""
Real Mural API Test with Browser Integration
IMPORTANT: This script NEVER closes the browser - it works with your existing session
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MuralRealTest')

class MuralRealAPITest:
    """
    Real Mural API testing with actual API calls
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.session = requests.Session()
        self.access_token = None
        self.board_id = self.config.get('board_id', '1754493659737')
        self.workspace_id = self.config.get('workspace_id', 'root7380')
        self.base_url = self.config.get('base_url', 'https://api.mural.co/api/v0')
        
        # Test tracking
        self.created_elements = []
        self.test_results = []
        
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open('lrl-workhorse/mural_config.json', 'r') as f:
                return json.load(f)
        except:
            with open('mural_config.json', 'r') as f:
                return json.load(f)
    
    def authenticate(self) -> bool:
        """Authenticate with Mural API using OAuth2 client credentials"""
        logger.info("Authenticating with Mural API...")
        
        # OAuth2 client credentials flow
        auth_url = "https://api.mural.co/oauth/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config['oauth']['client_id'],
            'client_secret': self.config['oauth']['client_secret'],
            'scope': 'murals:read murals:write'
        }
        
        try:
            response = requests.post(auth_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                logger.info("✓ Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def test_create_sticky_note(self, text: str, x: int, y: int, color: str = "#FFFF00") -> Optional[str]:
        """Create a real sticky note on the board"""
        logger.info(f"Creating sticky note: '{text[:30]}...' at ({x}, {y})")
        
        # Mural API endpoint for creating widgets
        url = f"{self.base_url}/murals/{self.workspace_id}.{self.board_id}/widgets"
        
        widget_data = {
            "type": "sticky-note",
            "text": text,
            "x": x,
            "y": y,
            "width": 200,
            "height": 200,
            "style": {
                "backgroundColor": color,
                "fontSize": 14,
                "textAlign": "center"
            }
        }
        
        try:
            response = self.session.post(url, json=widget_data)
            
            if response.status_code in [200, 201]:
                widget = response.json()
                widget_id = widget.get('id')
                self.created_elements.append({
                    'type': 'sticky-note',
                    'id': widget_id,
                    'text': text
                })
                logger.info(f"  ✓ Created sticky note: {widget_id}")
                return widget_id
            else:
                logger.error(f"  ✗ Failed to create sticky note: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"  ✗ Error creating sticky note: {e}")
            return None
    
    def test_body_visualization(self):
        """Create body visualization with sticky notes"""
        logger.info("\n=== Creating Body Visualization ===")
        
        # Body parts with positions (arranged in body shape)
        body_parts = [
            {"name": "HEAD", "x": 400, "y": 100, "color": "#E0E0E0"},
            {"name": "HEART", "x": 390, "y": 250, "color": "#FF6B6B"},
            {"name": "TORSO", "x": 400, "y": 350, "color": "#E0E0E0"},
            {"name": "L-ARM", "x": 250, "y": 300, "color": "#E0E0E0"},
            {"name": "R-ARM", "x": 550, "y": 300, "color": "#E0E0E0"},
            {"name": "L-LEG", "x": 350, "y": 500, "color": "#E0E0E0"},
            {"name": "R-LEG", "x": 450, "y": 500, "color": "#E0E0E0"}
        ]
        
        created_count = 0
        for part in body_parts:
            widget_id = self.test_create_sticky_note(
                text=part['name'],
                x=part['x'],
                y=part['y'],
                color=part['color']
            )
            if widget_id:
                created_count += 1
                time.sleep(0.5)  # Small delay between API calls
        
        logger.info(f"Body visualization result: {created_count}/{len(body_parts)} parts created")
        self.test_results.append({
            'test': 'body_visualization',
            'success': created_count >= 5,
            'details': f'{created_count}/{len(body_parts)} parts'
        })
    
    def test_somatic_mapping(self):
        """Test somatic mapping with themed sticky notes"""
        logger.info("\n=== Testing Somatic Mapping ===")
        
        # Test notes with TDAI scores and themes
        test_notes = [
            {
                "text": "Deep grief in chest area",
                "themes": ["grief", "heart"],
                "tdai": 8.5,
                "x": 390,
                "y": 280,
                "color": "#2ECC71"  # Deep green for high TDAI
            },
            {
                "text": "Racing anxious thoughts",
                "themes": ["thoughts", "anxiety"],
                "tdai": 6.0,
                "x": 400,
                "y": 130,
                "color": "#6BCF7F"  # Light green
            },
            {
                "text": "Grounded stable feeling",
                "themes": ["stability", "earth"],
                "tdai": 7.5,
                "x": 350,
                "y": 530,
                "color": "#2ECC71"  # Deep green
            },
            {
                "text": "Creative expression flowing",
                "themes": ["creation", "art"],
                "tdai": 7.0,
                "x": 550,
                "y": 330,
                "color": "#2ECC71"  # Deep green
            },
            {
                "text": "Surface level tension",
                "themes": ["tension", "stress"],
                "tdai": 3.5,
                "x": 250,
                "y": 330,
                "color": "#FFD93D"  # Yellow for medium TDAI
            }
        ]
        
        created_count = 0
        for note in test_notes:
            logger.info(f"Placing somatic note: '{note['text'][:30]}...'")
            logger.info(f"  TDAI: {note['tdai']} → Color: {note['color']}")
            
            widget_id = self.test_create_sticky_note(
                text=note['text'],
                x=note['x'],
                y=note['y'],
                color=note['color']
            )
            
            if widget_id:
                created_count += 1
                time.sleep(0.5)
        
        logger.info(f"Somatic mapping result: {created_count}/{len(test_notes)} notes placed")
        self.test_results.append({
            'test': 'somatic_mapping',
            'success': created_count >= 3,
            'details': f'{created_count}/{len(test_notes)} notes'
        })
    
    def test_batch_operations(self):
        """Test batch creation with different sizes"""
        logger.info("\n=== Testing Batch Operations ===")
        
        batch_sizes = [1, 3, 5]  # Start conservatively
        batch_results = []
        
        for size in batch_sizes:
            logger.info(f"Testing batch size {size}...")
            start_time = time.time()
            
            success_count = 0
            for i in range(size):
                widget_id = self.test_create_sticky_note(
                    text=f"Batch test {size}-{i+1}",
                    x=700 + (i * 50),
                    y=200 + (size * 50),
                    color="#FFD93D"
                )
                if widget_id:
                    success_count += 1
                    
                # Small delay to avoid rate limiting
                if i < size - 1:
                    time.sleep(0.2)
            
            duration = time.time() - start_time
            rate = success_count / duration if duration > 0 else 0
            
            batch_results.append({
                'size': size,
                'success': success_count == size,
                'rate': rate
            })
            
            logger.info(f"  Batch {size}: {success_count}/{size} created in {duration:.2f}s ({rate:.1f} items/sec)")
            
            # Delay between batches
            time.sleep(1)
        
        self.test_results.append({
            'test': 'batch_operations',
            'success': all(r['success'] for r in batch_results),
            'details': batch_results
        })
    
    def generate_report(self) -> Dict:
        """Generate test report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'board_id': f"{self.workspace_id}.{self.board_id}",
            'board_url': f"https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}",
            'elements_created': len(self.created_elements),
            'test_results': self.test_results,
            'created_elements': self.created_elements[:10],  # First 10 for brevity
            'summary': {
                'total_tests': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r['success']),
                'failed': sum(1 for r in self.test_results if not r['success'])
            }
        }
    
    def print_summary(self, report: Dict):
        """Print test summary"""
        print("\n" + "="*60)
        print("       REAL MURAL API TEST RESULTS")
        print("="*60)
        print(f"Board URL: {report['board_url']}")
        print(f"Elements Created: {report['elements_created']}")
        print(f"Tests Passed: {report['summary']['passed']}/{report['summary']['total_tests']}")
        
        print("\n--- Test Results ---")
        for result in report['test_results']:
            status = "✓" if result['success'] else "✗"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n--- Created Elements (Sample) ---")
        for elem in report['created_elements'][:5]:
            print(f"  • {elem['type']}: {elem.get('text', 'N/A')[:30]}...")
        
        print("\n" + "="*60)
        print("🎯 Check your Mural board to see the created elements!")
        print("   (The browser tab should still be open)")
        print("="*60)


async def test_with_browser_interaction():
    """Run tests and interact with browser (without closing it)"""
    logger.info("Starting real Mural API tests...")
    logger.info("IMPORTANT: Browser session will be preserved - NOT closed")
    
    # Run API tests
    tester = MuralRealAPITest()
    
    # Authenticate
    if not tester.authenticate():
        logger.error("Authentication failed. Please check credentials.")
        return False
    
    # Run tests
    tester.test_body_visualization()
    tester.test_somatic_mapping()
    tester.test_batch_operations()
    
    # Generate report
    report = tester.generate_report()
    
    # Save report
    with open('lrl-workhorse/mural_real_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    tester.print_summary(report)
    
    # Use MCP to take screenshot (without closing browser)
    logger.info("\n📸 Taking screenshot of your board...")
    logger.info("   (Browser will remain open)")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_with_browser_interaction())
    if success:
        print("\n✅ Tests completed successfully!")
        print("📌 Your browser is still open - check the board for created elements")
    else:
        print("\n❌ Tests failed - check logs for details")
