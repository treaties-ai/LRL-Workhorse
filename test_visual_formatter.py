#!/usr/bin/env python3
"""
Quick test script for the Visual Formatter
Run this to see the enhanced visual features in action
"""

from mural_visual_formatter import MuralVisualFormatter, VisualCategory

def test_simple_process():
    """Test a simple process flow with visual connections"""
    formatter = MuralVisualFormatter()
    
    print("\n" + "="*60)
    print("Testing Simple Process Flow with Visual Connections")
    print("="*60)
    
    # Clear board first
    formatter.clear_board()
    
    # Create a simple process flow
    process_steps = [
        {"text": "Customer Request", "category": VisualCategory.START},
        {"text": "Check Inventory", "category": VisualCategory.PROCESS},
        {"text": "Process Order", "category": VisualCategory.PROCESS},
        {"text": "Ship Product", "category": VisualCategory.COMPLETE}
    ]
    
    formatter.create_process_flow(process_steps, start_x=200, start_y=300)
    
    print("\n✅ Process flow created with arrow connections!")
    print("Check your MURAL board to see the visual connections")

def test_mixed_layout():
    """Test a combination of different visual elements"""
    formatter = MuralVisualFormatter()
    
    print("\n" + "="*60)
    print("Testing Mixed Visual Layout")
    print("="*60)
    
    # Clear board
    formatter.clear_board()
    
    # 1. Create a small mind map at top
    branches = {
        "north": ["Objective 1"],
        "east": ["Resource A"],
        "south": ["Risk Factor"],
        "west": ["Team Lead"]
    }
    formatter.create_mind_map("Project Alpha", branches, start_x=400, start_y=300)
    
    # 2. Add a simple kanban below
    columns = {
        "Pending": ["Review docs", "Get approval"],
        "Active": ["Build prototype"],
        "Complete": ["Initial research"]
    }
    formatter.create_kanban_board(columns, start_x=200, start_y=600)
    
    print("\n✅ Mixed layout created!")
    print("You should see a mind map and kanban board with visual variety")

def test_emoji_categories():
    """Test different emoji categories for visual interest"""
    formatter = MuralVisualFormatter()
    
    print("\n" + "="*60)
    print("Testing Emoji Categories")
    print("="*60)
    
    # Clear board
    formatter.clear_board()
    
    # Create widgets with different categories
    y_position = 200
    x_position = 100
    
    categories_to_test = [
        (VisualCategory.START, "Project Kickoff"),
        (VisualCategory.PROCESS, "Development Phase"),
        (VisualCategory.WARNING, "Budget Review Needed"),
        (VisualCategory.ERROR, "Blocker Found"),
        (VisualCategory.COMPLETE, "Milestone Achieved"),
        (VisualCategory.IDEA, "Innovation Opportunity"),
        (VisualCategory.GOAL, "Q1 Target"),
        (VisualCategory.PRIORITY, "Critical Path Item"),
        (VisualCategory.TEAM, "Team Meeting"),
        (VisualCategory.TIME, "Deadline Approaching"),
        (VisualCategory.MONEY, "Budget Allocation")
    ]
    
    for i, (category, text) in enumerate(categories_to_test):
        # Create in a grid pattern
        row = i // 4
        col = i % 4
        x = x_position + (col * 250)
        y = y_position + (row * 200)
        
        formatter.create_widget(
            text,
            x,
            y,
            category=category
        )
    
    print("\n✅ Created widgets with all emoji categories!")
    print("You should see various emojis providing visual categorization")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎨 MURAL Visual Formatter Test Suite")
    print("="*80)
    print("\nChoose a test to run:")
    print("1. Simple Process Flow")
    print("2. Mixed Layout (Mind Map + Kanban)")
    print("3. Emoji Categories Demo")
    print("4. Run All Tests")
    print("-"*80)
    
    # For automated testing, run test 1
    choice = "1"
    
    if choice == "1":
        test_simple_process()
    elif choice == "2":
        test_mixed_layout()
    elif choice == "3":
        test_emoji_categories()
    elif choice == "4":
        test_simple_process()
        print("\n" + "-"*60)
        input("Press Enter to continue to next test...")
        test_mixed_layout()
        print("\n" + "-"*60)
        input("Press Enter to continue to next test...")
        test_emoji_categories()
    
    print("\n" + "="*80)
    print("Testing complete!")
    print("Visit your MURAL board to see the results")
    print("="*80)
