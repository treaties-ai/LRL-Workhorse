# MURAL Workflow Playbook
*Step-by-step procedures for common tasks*

## 🚀 Quick Start (Fresh Session)

### Initial Setup Checklist
```bash
# 1. Navigate to project
cd lrl-workhorse

# 2. Check/refresh authentication
python3 mural_oauth_setup.py
# Browser will open → Authorize → Token saved to .env

# 3. Verify system health
python3 test_spacing_quality.py
# Should see: "9/9 tests passed"

# 4. Create demonstration
python3 mural_visual_formatter_v2.py
# Creates full demo with all layout types
```

## 📋 Common Workflows

### Workflow 1: Create a Simple Process Flow
```python
from mural_visual_formatter_v2 import MuralVisualFormatterV2, VisualCategory

# Initialize formatter
formatter = MuralVisualFormatterV2()

# Clear board (optional)
formatter.clear_board()

# Define process steps
steps = [
    {"text": "Receive Request", "category": VisualCategory.START},
    {"text": "Validate Data", "category": VisualCategory.PROCESS},
    {"text": "Process Payment", "category": VisualCategory.PROCESS},
    {"text": "Send Receipt", "category": VisualCategory.COMPLETE}
]

# Create the flow
formatter.create_process_flow(steps, start_x=100, start_y=200)
```

### Workflow 2: Create Multiple Layouts Without Overlap
```python
from mural_visual_formatter_v2 import MuralVisualFormatterV2, LayoutZone

formatter = MuralVisualFormatterV2()
formatter.clear_board()

# Each layout in its own zone - no overlaps!
formatter.create_process_flow(process_steps, LayoutZone.PROCESS_FLOW)
formatter.create_mind_map("Central Idea", branches, LayoutZone.MIND_MAP)
formatter.create_kanban_board(columns, LayoutZone.KANBAN)
formatter.create_decision_tree("Question?", options, LayoutZone.DECISION_TREE)
```

### Workflow 3: Custom Widget Placement
```python
# Place individual widgets with collision detection
formatter.create_widget(
    text="Important Note",
    x=300,
    y=400,
    size=WidgetSize.STANDARD,
    category=VisualCategory.WARNING,
    check_collision=True  # Will auto-reposition if needed
)
```

## 🔧 Problem-Solving Patterns

### Pattern: Widget Overlap Issues
```python
# PROBLEM: Widgets overlapping
# OLD WAY (V1):
formatter.create_widget("Text", 100, 100)  # Might overlap!

# NEW WAY (V2):
# Uses WidgetRegistry.check_collision() automatically
formatter = MuralVisualFormatterV2()  # Has collision detection
formatter.create_widget("Text", 100, 100)  # Auto-repositions if collision
```

### Pattern: Visual Monotony
```python
# PROBLEM: All widgets look the same
# SOLUTION: Apply VisualCategory emojis

# Boring:
widget = {"text": "Task Complete"}

# Engaging:
widget = {"text": "Task Complete", "category": VisualCategory.COMPLETE}
# Shows as: "✅ Task Complete"
```

### Pattern: Layout Chaos
```python
# PROBLEM: Different layouts interfering with each other
# SOLUTION: Use LayoutZone boundaries

# Chaotic (no zones):
formatter.create_process_flow(steps, 100, 100)
formatter.create_mind_map(center, branches, 200, 200)  # Might overlap!

# Organized (with zones):
formatter.create_process_flow(steps, LayoutZone.PROCESS_FLOW)
formatter.create_mind_map(center, branches, LayoutZone.MIND_MAP)
```

### Pattern: Token Expiration
```bash
# SYMPTOM: 401 errors
[01:28:55] ❌ Failed to create widget: 401

# SOLUTION: Refresh token
python3 mural_oauth_setup.py
# Browser opens → Authorize → New token saved
```

## 🧪 Testing Procedures

### Test 1: Verify Spacing Quality
```bash
python3 test_spacing_quality.py

# Expected output:
# TEST 1: Single Widget Placement: ✅ PASSED
# TEST 2: Collision Detection: ✅ PASSED
# TEST 3: Minimum Spacing: ✅ PASSED
# TEST 4: Zone Boundaries: ✅ PASSED
# TEST 5: Arrow Alignment: ✅ PASSED
# TEST 6: Progressive Complexity: ✅ PASSED
# Tests Passed: 9/9
```

### Test 2: Check Collision Detection
```python
# Place two widgets at same location
formatter.create_widget("Widget 1", 100, 100)
formatter.create_widget("Widget 2", 100, 100)
# Should see: "Collision detected at (100, 100), moved to (new_x, new_y)"
```

### Test 3: Validate Zone Separation
```python
# Create layouts in different zones
formatter.demo_with_zones()
# Check board - layouts should be in distinct areas
```

## 📊 Layout Templates Reference

### Process Flow Template
```python
steps = [
    {"text": "Start", "category": VisualCategory.START},
    {"text": "Step 1", "category": VisualCategory.PROCESS},
    {"text": "Step 2", "category": VisualCategory.PROCESS},
    {"text": "Complete", "category": VisualCategory.COMPLETE}
]
formatter.create_process_flow(steps)
```

### Mind Map Template
```python
branches = {
    "north": ["Goal 1", "Goal 2"],
    "east": ["Resource 1", "Resource 2"],
    "south": ["Risk 1", "Risk 2"],
    "west": ["Team A", "Team B"]
}
formatter.create_mind_map("Project Hub", branches)
```

### Kanban Board Template
```python
columns = {
    "To Do": ["Task A", "Task B", "Task C"],
    "In Progress": ["Task D", "Task E"],
    "Done": ["Task F", "Task G"]
}
formatter.create_kanban_board(columns)
```

### Decision Tree Template
```python
branches = [
    {"condition": "Yes", "outcome": "Proceed with plan"},
    {"condition": "No", "outcome": "Revise approach"}
]
formatter.create_decision_tree("Approve budget?", branches)
```

## 🎯 Best Practices

### DO's
✅ Always use V2 formatter (`mural_visual_formatter_v2.py`)
✅ Specify zones when creating multiple layouts
✅ Use VisualCategory emojis for visual variety
✅ Run spacing tests after major changes
✅ Clear board before creating new layouts
✅ Check token validity at session start

### DON'Ts
❌ Don't use V1 formatter (has overlap issues)
❌ Don't disable collision detection
❌ Don't place widgets without zones in multi-layout boards
❌ Don't ignore 401 errors (refresh token immediately)
❌ Don't use unsanitized text (remove box characters)

## 🚨 Emergency Procedures

### Board is Unreadable
```python
# 1. Clear everything
formatter.clear_board()

# 2. Use zoned demo (guaranteed no overlaps)
formatter.demo_with_zones()
```

### Widgets Not Creating
```bash
# Check token
python3 mural_oauth_setup.py

# Verify API is working
python3 test_spacing_quality.py
```

### Overlapping Despite V2
```python
# Check registry is working
print(f"Widgets tracked: {len(formatter.registry.widgets)}")

# Ensure collision detection is on
formatter.create_widget(..., check_collision=True)  # Default is True
```

## 📈 Performance Optimization

### Fast Board Clear
```python
# Instead of deleting one-by-one
formatter.clear_board()  # Batch deletes all widgets
```

### Efficient Multi-Layout Creation
```python
# Use zones to prevent collision checks between layouts
formatter.create_process_flow(steps, LayoutZone.PROCESS_FLOW)
# Each zone is independent - faster placement
```

### Batch Widget Creation
```python
# Create all widgets, then pause
for widget in widgets:
    formatter.create_widget(...)
time.sleep(1)  # Let API catch up
```

## 🔍 Debugging Checklist

When things go wrong:

1. **Check Authentication**
   ```bash
   python3 mural_oauth_setup.py
   ```

2. **Verify V2 is being used**
   ```python
   # Should import from v2
   from mural_visual_formatter_v2 import MuralVisualFormatterV2
   ```

3. **Test Collision Detection**
   ```python
   # Should show collision messages
   formatter.create_widget("Test", 100, 100)
   formatter.create_widget("Test2", 100, 100)
   ```

4. **Validate Spacing**
   ```bash
   python3 test_spacing_quality.py
   ```

5. **Check Console Output**
   - Look for "Collision detected" messages
   - Check for 401 errors
   - Verify "Created:" success messages

---
*Use this playbook for consistent, reliable MURAL board creation. When in doubt, run the tests!*
