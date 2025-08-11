#!/usr/bin/env python3
"""
MURAL Professional Formatter
Takes your content and formats it professionally on the MURAL board
No all-caps, subtle and elegant formatting only
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple

# Load environment variables
load_dotenv('.env')

class MuralProfessionalFormatter:
    """Format and layout content professionally on MURAL"""
    
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
        
        # Professional layout parameters
        self.STANDARD_WIDTH = 200
        self.STANDARD_HEIGHT = 150
        self.HEADER_WIDTH = 250
        self.HEADER_HEIGHT = 100
        self.HORIZONTAL_SPACING = 250
        self.VERTICAL_SPACING = 200
        self.SECTION_SPACING = 300  # Extra space between sections
        
        print("\n" + "="*80)
        print("MURAL Professional Formatter")
        print("="*80)
        print("Elegant, subtle formatting for professional presentation")
        print(f"Board: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}")
        print("-"*80)
    
    def log(self, message, level="INFO"):
        """Simple logging with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "FORMAT": "📝",
            "LAYOUT": "📐"
        }
        print(f"[{timestamp}] {symbols.get(level, '•')} {message}")
    
    def format_text(self, text: str, text_type: str = "body") -> str:
        """
        Apply professional formatting based on text type
        NO ALL CAPS - subtle and elegant only
        """
        # Remove any existing all-caps
        if text.isupper() and len(text) > 3:
            text = text.title()  # Convert to Title Case
        
        if text_type == "header":
            # Title Case for headers
            formatted = self.to_title_case(text)
            # Could add underline with dashes if multi-line supported
            return formatted
            
        elif text_type == "subheader":
            # Sentence case with colon if appropriate
            formatted = self.to_sentence_case(text)
            if not formatted.endswith((':','.','?','!')):
                formatted += ":"
            return formatted
            
        elif text_type == "bullet":
            # Add bullet point if not present
            if not text.startswith(('•', '-', '*', '·')):
                formatted = f"• {text}"
            else:
                formatted = text
            # Ensure proper sentence ending
            if not formatted.endswith(('.', '!', '?', ':')):
                formatted += "."
            return self.to_sentence_case(formatted)
            
        elif text_type == "number":
            # Numbered list formatting
            if not text[0].isdigit():
                return f"1. {self.to_sentence_case(text)}"
            return self.to_sentence_case(text)
            
        elif text_type == "note":
            # Subtle note formatting
            formatted = self.to_sentence_case(text)
            if not formatted.startswith('Note:'):
                formatted = f"Note: {formatted}"
            return formatted
            
        else:  # body
            # Standard sentence formatting
            return self.to_sentence_case(text)
    
    def to_title_case(self, text: str) -> str:
        """Convert to Title Case properly"""
        # List of words to keep lowercase
        lowercase_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Always capitalize first and last word
            if i == 0 or i == len(words) - 1:
                result.append(word.capitalize())
            # Keep lowercase for articles/prepositions unless they start the text
            elif word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)
    
    def to_sentence_case(self, text: str) -> str:
        """Convert to sentence case with proper capitalization"""
        if not text:
            return text
        
        # Capitalize first letter, rest lowercase (preserve acronyms)
        sentences = text.split('. ')
        formatted_sentences = []
        
        for sentence in sentences:
            if sentence:
                # Preserve acronyms (all caps words of 2-5 letters)
                words = sentence.split()
                formatted_words = []
                for i, word in enumerate(words):
                    if i == 0:
                        formatted_words.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
                    elif word.isupper() and 2 <= len(word) <= 5:
                        formatted_words.append(word)  # Keep acronyms
                    else:
                        formatted_words.append(word.lower())
                formatted_sentences.append(' '.join(formatted_words))
        
        return '. '.join(formatted_sentences)
    
    def sanitize_for_api(self, text: str) -> str:
        """Remove problematic Unicode characters"""
        replacements = {
            '━': '─', '─': '-', '│': '|', '•': '•',
            '€': 'EUR', '™': 'TM', '®': '(R)',
            '"': '"', '"': '"', ''': "'", ''': "'"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove zero-width and control characters
        text = ''.join(char for char in text if ord(char) >= 32)
        return text
    
    def create_widget(self, text: str, x: int, y: int, width: int = None, height: int = None) -> bool:
        """Create a single widget on the board"""
        endpoint = f"{self.base_url}/murals/{self.combined_id}/widgets/sticky-note"
        
        if width is None:
            width = self.STANDARD_WIDTH
        if height is None:
            height = self.STANDARD_HEIGHT
        
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
    
    def format_content_section(self, section_data: Dict) -> List[Dict]:
        """
        Format a section of content with proper hierarchy
        
        section_data = {
            "title": "Section Title",
            "type": "header|body|list",
            "items": ["item1", "item2", ...] or "single text"
        }
        """
        formatted_items = []
        
        title = section_data.get("title", "")
        section_type = section_data.get("type", "body")
        items = section_data.get("items", [])
        
        # Add section header if provided
        if title:
            formatted_title = self.format_text(title, "header")
            formatted_items.append({
                "text": formatted_title,
                "type": "header"
            })
        
        # Format items based on type
        if isinstance(items, str):
            items = [items]
        
        for i, item in enumerate(items):
            if section_type == "list":
                formatted_text = self.format_text(item, "bullet")
            elif section_type == "numbered":
                formatted_text = self.format_text(f"{i+1}. {item}", "number")
            else:
                formatted_text = self.format_text(item, "body")
            
            formatted_items.append({
                "text": formatted_text,
                "type": section_type
            })
        
        return formatted_items
    
    def create_professional_layout(self, content_sections: List[Dict]):
        """
        Create a professional layout with formatted content
        
        content_sections = [
            {
                "title": "Section Name",
                "type": "header|body|list|numbered",
                "items": ["content1", "content2", ...]
            },
            ...
        ]
        """
        self.log("\n" + "="*60, "INFO")
        self.log("Creating Professional Layout", "LAYOUT")
        self.log("="*60, "INFO")
        
        # Clear board first
        self.clear_board()
        time.sleep(2)
        
        # Starting position
        current_x = 100
        current_y = 200
        max_items_per_row = 5
        
        for section_idx, section in enumerate(content_sections):
            self.log(f"\nFormatting section: {section.get('title', 'Untitled')}", "FORMAT")
            
            # Format the section content
            formatted_items = self.format_content_section(section)
            
            # Create widgets for this section
            for i, item in enumerate(formatted_items):
                # Headers get their own row
                if item["type"] == "header":
                    if i > 0:  # If not the first item, move to new row
                        current_y += self.SECTION_SPACING
                    current_x = 100
                    
                    # Create header widget (wider)
                    self.create_widget(
                        item["text"],
                        current_x,
                        current_y,
                        self.HEADER_WIDTH,
                        self.HEADER_HEIGHT
                    )
                    current_y += self.VERTICAL_SPACING
                    current_x = 100
                    
                else:
                    # Regular items in grid
                    col = (i - 1) % max_items_per_row if formatted_items[0]["type"] == "header" else i % max_items_per_row
                    
                    if col == 0 and i > 0:
                        current_y += self.VERTICAL_SPACING
                        current_x = 100
                    
                    widget_x = current_x + (col * self.HORIZONTAL_SPACING)
                    
                    self.create_widget(
                        item["text"],
                        widget_x,
                        current_y
                    )
            
            # Add extra spacing between sections
            current_y += self.SECTION_SPACING
            current_x = 100
            time.sleep(0.5)  # Small delay between sections
        
        self.log("\n✅ Professional layout complete!", "SUCCESS")
        self.log(f"View your board: https://app.mural.co/t/{self.workspace_id}/m/{self.workspace_id}/{self.board_id}", "INFO")
    
    def demo_professional_formatting(self):
        """Demonstrate professional formatting with sample content"""
        demo_content = [
            {
                "title": "Project Status Overview",
                "type": "list",
                "items": [
                    "Implementation phase complete",
                    "Testing in progress with 85% coverage",
                    "Documentation updates pending review",
                    "Deployment scheduled for next Tuesday"
                ]
            },
            {
                "title": "Key Metrics",
                "type": "body",
                "items": [
                    "Response time: 250ms average",
                    "Uptime: 99.9% this month",
                    "User satisfaction: 4.5/5.0",
                    "Active users: 1,250"
                ]
            },
            {
                "title": "Next Steps",
                "type": "numbered",
                "items": [
                    "Complete remaining test cases",
                    "Review and update documentation",
                    "Conduct final security audit",
                    "Prepare deployment checklist",
                    "Schedule team retrospective"
                ]
            },
            {
                "title": "Notes and Reminders",
                "type": "body",
                "items": [
                    "Remember to update the changelog",
                    "Client meeting scheduled for Friday",
                    "New team member onboarding Monday",
                    "Quarterly review due end of month"
                ]
            }
        ]
        
        self.create_professional_layout(demo_content)


def main():
    """Main execution"""
    formatter = MuralProfessionalFormatter()
    
    # You can either run the demo or provide your own content
    print("\nRunning professional formatting demo...")
    print("(Replace demo_content with your own content in the script)")
    
    formatter.demo_professional_formatting()


if __name__ == "__main__":
    main()
