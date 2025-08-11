# MURAL Formatting Next Steps - From Yellow Stickies to Visual Excellence

## Current State Analysis

### What We Have Now
Looking at the screenshot you provided, we successfully created sticky notes but they all have:
- **Same color**: All yellow
- **Text truncation**: Some content is cut off
- **No visual hierarchy**: Can't distinguish headers from content
- **Poor layout**: Random positioning, no organizational structure
- **Limited readability**: Multi-line text not displaying optimally

### What We Need
- **Color coding**: Different colors for different content types
- **Dynamic sizing**: Adjust widget size based on content
- **Spatial organization**: Anatomical layout for body parts
- **Visual hierarchy**: Clear distinction between categories
- **Better text display**: Optimized for multi-line content

---

## Challenge 1: Adding Colors

### The Problem
- Colors CANNOT be set during widget creation
- Must use PATCH request after creation
- Need to track widget IDs for updates

### Solution Approach
```python
def create_and_color_sticky(text, x, y, color):
    """Create sticky note then immediately update its color"""
    
    # Step 1: Create the sticky (returns widget ID)
    create_response = requests.post(
        endpoint,
        headers=headers,
        json={
            "shape": "rectangle",
            "text": sanitize_for_mural_display(text),
            "x": x,
            "y": y,
            "width": 138,
            "height": 138
        }
    )
    
    if create_response.status_code == 201:
        widget_id = create_response.json()['value']['id']
        
        # Step 2: Update the color
        patch_endpoint = f"{base_url}/widgets/{widget_id}"
        patch_response = requests.patch(
            patch_endpoint,
            headers=headers,
            json={
                "style": {
                    "backgroundColor": color  # e.g., "#FF5733"
                }
            }
        )
        
        return widget_id, patch_response.status_code == 200
```

### Color Scheme Proposal
```python
COLOR_SCHEME = {
    # Body Parts
    "HEAD": "#4A90E2",      # Blue
    "HEART": "#E94B3C",     # Red
    "TORSO": "#6B5B95",     # Purple
    "ARMS": "#F0AD4E",      # Orange
    "LEGS": "#5CB85C",      # Green
    
    # TDAI Scores
    "TDAI_HIGH": "#D32F2F",     # Dark Red (8-10)
    "TDAI_MEDIUM": "#FFA726",   # Orange (5-7)
    "TDAI_LOW": "#66BB6A",      # Green (0-4)
    
    # Categories
    "THREAT": "#B71C1C",        # Deep Red
    "COMPANY": "#1565C0",       # Deep Blue
    "EMOTION": "#7B1FA2",       # Deep Purple
    "GROUNDING": "#2E7D32",     # Deep Green
}
```

---

## Challenge 2: Dynamic Widget Sizing

### Current Issues
- Fixed 138x138 size truncates longer text
- No differentiation between headers and content
- Multi-line text gets cut off

### Solution Approach
```python
def calculate_widget_size(text):
    """Calculate optimal widget size based on text content"""
    
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines)
    line_count = len(lines)
    
    # Base calculations
    char_width = 7  # Approximate pixels per character
    line_height = 20  # Approximate pixels per line
    
    # Calculate dimensions
    width = min(max(138, max_line_length * char_width + 20), 300)
    height = min(max(138, line_count * line_height + 40), 400)
    
    return width, height
```

### Size Categories
```python
SIZE_PRESETS = {
    "SMALL": (138, 138),      # Single line, short text
    "MEDIUM": (200, 150),      # 2-3 lines, moderate text
    "LARGE": (250, 200),       # Complex content
    "HEADER": (300, 100),      # Wide headers
    "BODY_PART": (150, 150),   # Body visualization
    "DETAIL": (200, 250),      # Detailed descriptions
}
```

---

## Challenge 3: Spatial Organization

### Body Visualization Layout
```python
def calculate_body_positions():
    """Calculate anatomically correct positions for body parts"""
    
    center_x = 400
    center_y = 400
    
    positions = {
        "HEAD": (center_x, center_y - 150),
        "HEART": (center_x, center_y),
        "TORSO": (center_x, center_y + 50),
        "LEFT_ARM": (center_x - 100, center_y),
        "RIGHT_ARM": (center_x + 100, center_y),
        "LEFT_LEG": (center_x - 50, center_y + 150),
        "RIGHT_LEG": (center_x + 50, center_y + 150),
    }
    
    return positions
```

### Ring-Based Layout for Categories
```python
def calculate_ring_positions(items, center_x, center_y, radius):
    """Arrange items in a ring around a center point"""
    
    positions = []
    angle_step = 2 * math.pi / len(items)
    
    for i, item in enumerate(items):
        angle = i * angle_step
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions.append((x, y))
    
    return positions
```

---

## Challenge 4: Text Display Optimization

### Current Problems
- Newlines preserved but not displayed well
- Text hierarchy not visible
- Long text gets truncated

### Solution Approach
```python
def format_text_for_display(text, widget_type):
    """Format text optimally for MURAL display"""
    
    if widget_type == "HEADER":
        # All caps, single line
        return text.upper()[:50]
    
    elif widget_type == "BODY_PART":
        # Name only, centered
        return text.strip().upper()
    
    elif widget_type == "DETAIL":
        # Preserve structure, add visual breaks
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            if ':' in line:
                # Emphasize key-value pairs
                key, value = line.split(':', 1)
                formatted.append(f"{key.upper()}:{value}")
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    elif widget_type == "TDAI_SCORE":
        # Extract and highlight score
        import re
        match = re.search(r'TDAI:\s*([\d.]+)', text)
        if match:
            score = float(match.group(1))
            return f"TDAI SCORE\n{score}/10\n{get_tdai_label(score)}"
        
    return text
```

---

## Implementation Roadmap

### Phase 1: Color Implementation (Immediate)
1. Add PATCH functionality to update colors
2. Implement color scheme based on content type
3. Create color legend sticky note

### Phase 2: Size Optimization (Next)
1. Implement dynamic size calculation
2. Test with various content types
3. Optimize for readability

### Phase 3: Layout Structure (Following)
1. Implement body visualization positioning
2. Create ring layouts for categories
3. Add spatial grouping for related content

### Phase 4: Text Enhancement (Final)
1. Optimize text formatting for display
2. Add visual hierarchy within text
3. Implement smart truncation

---

## Example: Complete Formatted Widget

```python
def create_formatted_widget(content_type, text, position_index):
    """Create a fully formatted widget with color, size, and position"""
    
    # Determine color
    if "TDAI" in text:
        score = extract_tdai_score(text)
        color = get_tdai_color(score)
    elif content_type in BODY_PARTS:
        color = COLOR_SCHEME[content_type]
    else:
        color = COLOR_SCHEME.get(content_type, "#FFEB3B")  # Default yellow
    
    # Calculate size
    if content_type == "HEADER":
        width, height = SIZE_PRESETS["HEADER"]
    elif content_type in BODY_PARTS:
        width, height = SIZE_PRESETS["BODY_PART"]
    else:
        width, height = calculate_widget_size(text)
    
    # Determine position
    if content_type in BODY_PARTS:
        x, y = BODY_POSITIONS[content_type]
    else:
        x, y = calculate_grid_position(position_index)
    
    # Format text
    formatted_text = format_text_for_display(text, content_type)
    
    # Create widget
    widget_id = create_widget(formatted_text, x, y, width, height)
    
    # Apply color
    update_widget_color(widget_id, color)
    
    return widget_id
```

---

## Expected Final Result

### Visual Improvements
- **Color-coded categories**: Instant visual recognition
- **Proper text display**: All content readable
- **Anatomical layout**: Body parts in correct positions
- **Visual hierarchy**: Headers stand out from content
- **Professional appearance**: Organized, clean, purposeful

### User Experience
- **Faster comprehension**: Colors convey meaning instantly
- **Better navigation**: Spatial organization aids understanding
- **Clearer relationships**: Related items grouped visually
- **Enhanced readability**: Optimized text formatting

---

## Testing Strategy

### Incremental Rollout
1. **Test color updates**: Single sticky color change
2. **Test size variations**: Different preset sizes
3. **Test positioning**: Basic grid layout
4. **Test combinations**: Full formatting stack
5. **Test at scale**: Multiple formatted widgets

### Success Criteria
- [ ] All widgets have appropriate colors
- [ ] Text is fully readable (no truncation)
- [ ] Body parts in anatomical positions
- [ ] TDAI scores color-coded by severity
- [ ] Overall layout is organized and professional

---

## Files to Create Next

1. **mural_formatting_engine.py** - Core formatting logic
2. **mural_color_manager.py** - Color scheme management
3. **mural_layout_calculator.py** - Position calculations
4. **mural_text_formatter.py** - Text optimization
5. **mural_formatted_test.py** - Complete test implementation

---

*This document outlines the path from our current yellow sticky notes to a fully formatted, professional MURAL visualization. Each challenge has been identified with specific solutions ready for implementation.*
