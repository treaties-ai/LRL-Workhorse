# MURAL Session Reconstruction Guide
*How to quickly achieve current capability level in a new context window*

## 🎯 Quick Context Loading Sequence

### Step 1: Understand the Current State (2 minutes)
```bash
# Read this first - it's your roadmap
cat MURAL_IMPLEMENTATION_CONTEXT.md

# Key takeaway: V2 is production, V1 had overlaps, use collision detection
```

### Step 2: Verify Setup (1 minute)
```bash
# Check you're in the right place
pwd  # Should be in lrl-workhorse

# Verify key files exist
ls mural_visual_formatter_v2.py
ls test_spacing_quality.py
```

### Step 3: Test the System (3 minutes)
```bash
# Run quality tests to understand what "working" means
python3 test_spacing_quality.py

# Should see 9/9 tests pass - this validates your understanding
```

### Step 4: See It In Action (5 minutes)
```bash
# Refresh token if needed (401 errors)
python3 mural_oauth_setup.py

# Create a demo to see the solution
python3 mural_visual_formatter_v2.py

# Watch the output - notice "Collision detected" messages
```

## 🧠 Key Concepts to Internalize

### The Core Problem & Solution
```
PROBLEM: Widgets overlapped, creating unreadable clusters
ROOT CAUSE: No spatial awareness in V1

SOLUTION: WidgetRegistry tracks all placements
MECHANISM: find_safe_position() uses circular search
RESULT: 100% overlap-free layouts
```

### The Critical Classes
```python
# 1. WidgetBounds - The math
@dataclass
class WidgetBounds:
    # Has overlaps_with() method for collision detection
    # Properties: left, right, top, bottom

# 2. WidgetRegistry - The tracker  
class WidgetRegistry:
    # Maintains list of all widget bounds
    # check_collision() prevents overlaps
    # find_safe_position() resolves conflicts

# 3. LayoutZone - The organizer
class LayoutZone(Enum):
    # Predefined areas prevent layout interference
    # Each zone is independent
```

### The Visual System
```python
# Since we can't change colors, we use:
VisualCategory.START = "🟢"    # Emojis for color
WidgetSize.HERO = (300, 120)   # Size for hierarchy
"→" as widgets                  # Arrows for connections
```

## 📚 Essential File Reading Order

### Tier 1: Must Read (Understand constraints)
1. `MURAL_COLOR_LIMITATION_FINDINGS.md` - Why we can't change colors
2. `MURAL_IMPLEMENTATION_CONTEXT.md` - Complete system overview

### Tier 2: Core Implementation (See the solution)
3. `mural_visual_formatter_v2.py` - Read these methods:
   - `find_safe_position()` - How collision resolution works
   - `create_widget()` - How widgets are placed
   - `WidgetBounds.overlaps_with()` - The collision math

### Tier 3: Validation (Understand quality)
4. `test_spacing_quality.py` - What we test for
5. `MURAL_WORKFLOW_PLAYBOOK.md` - Common patterns

### Tier 4: Deep Understanding (Optional but valuable)
6. `mural_visual_formatter.py` - V1 to see what NOT to do
7. `MURAL_TECHNICAL_DECISIONS.md` - The "why" behind everything

## 🔍 Quick Competency Check

Answer these to verify understanding:

### Q1: Why do widgets overlap in V1?
**A**: No collision detection - widgets placed at exact coordinates regardless of existing widgets

### Q2: How does find_safe_position() work?
**A**: Searches in expanding circles (50px radius increments) testing positions every 30 degrees until finding non-colliding spot

### Q3: What prevents different layouts from interfering?
**A**: LayoutZone enum defines non-overlapping areas for each layout type

### Q4: How do we show connections without lines?
**A**: Small arrow widgets (80x40px) positioned between related widgets

### Q5: Why 30px minimum spacing?
**A**: Testing showed optimal balance - 20px too tight, 50px too sparse

## 💡 Critical Code Patterns

### Pattern 1: Always Use V2
```python
# WRONG
from mural_visual_formatter import MuralVisualFormatter  # V1

# RIGHT
from mural_visual_formatter_v2 import MuralVisualFormatterV2  # V2
```

### Pattern 2: Use Zones for Multiple Layouts
```python
# WRONG - Layouts will interfere
formatter.create_process_flow(steps, 100, 100)
formatter.create_mind_map(center, branches, 200, 200)

# RIGHT - Each in its zone
formatter.create_process_flow(steps, LayoutZone.PROCESS_FLOW)
formatter.create_mind_map(center, branches, LayoutZone.MIND_MAP)
```

### Pattern 3: Trust Collision Detection
```python
# Don't try to manually avoid collisions
# Just place where you want - system handles it
formatter.create_widget("Text", desired_x, desired_y)
# If collision, automatically moves to safe position
```

## 🚀 Achieving Current Fluidity

### Mental Model
Think of the board as having:
1. **Zones** - Separate areas for different layout types
2. **Registry** - Knows where everything is
3. **Collision Detection** - Automatically prevents overlaps
4. **Visual System** - Emojis + sizes + arrows for variety

### Command Mastery
```bash
# The three essential commands
python3 mural_oauth_setup.py        # Fix auth issues
python3 test_spacing_quality.py     # Verify system
python3 mural_visual_formatter_v2.py # Create boards
```

### Problem-Solution Reflexes
- See 401 error → Run oauth setup
- Widgets overlapping → Check using V2
- Layouts interfering → Add LayoutZone
- Board looks monotone → Add VisualCategory

## 🎓 Progressive Understanding Levels

### Level 1: Basic Operation (5 minutes)
- Can run the three essential commands
- Knows V2 is production, V1 is legacy
- Understands emojis = colors

### Level 2: Problem Solving (15 minutes)  
- Understands collision detection mechanism
- Can diagnose overlap issues
- Knows how zones prevent interference

### Level 3: Full Fluidity (30 minutes)
- Can explain circular search algorithm
- Understands all technical decisions
- Can modify and extend the system

## 🔧 Debugging Intuition

### When widgets overlap:
1. Check importing from `_v2`
2. Verify collision detection enabled
3. Check registry has widgets

### When layouts interfere:
1. Ensure using LayoutZone
2. Check zone boundaries
3. Verify no hardcoded positions

### When visual monotony:
1. Add VisualCategory emojis
2. Vary WidgetSize
3. Include arrow connectors

## 📝 Context Window Checklist

When starting fresh:
- [ ] Read MURAL_IMPLEMENTATION_CONTEXT.md
- [ ] Run test_spacing_quality.py (9/9 pass?)
- [ ] Try creating a simple widget
- [ ] Notice collision detection messages
- [ ] Create multi-zone layout
- [ ] Verify no overlaps on board

## 🎯 Success Indicators

You've achieved current capability when:
1. Tests pass 9/9 consistently
2. No overlapping widgets ever
3. Multiple layouts coexist peacefully
4. Visual variety through emojis/sizes
5. Can diagnose issues quickly
6. Understand the "why" not just "how"

## 💬 Key Phrases That Trigger Understanding

- "Collision detection" → WidgetRegistry + find_safe_position()
- "Visual variety" → Emoji categories + size hierarchy
- "No overlaps" → V2 with WidgetBounds math
- "Zone management" → LayoutZone enum
- "Arrow connections" → Small widgets as connectors
- "30px spacing" → Minimum buffer for readability

## 🚨 Anti-Patterns to Avoid

❌ Using V1 formatter (mural_visual_formatter.py)
❌ Disabling collision detection
❌ Hardcoding positions without zones
❌ Ignoring 401 errors
❌ Placing widgets without formatter class

## 📈 Performance Expectations

- Widget creation: ~1 second each
- Board clear: 30-45 seconds
- Test suite: ~2 minutes
- Full demo: ~3 minutes
- Token refresh: ~5 seconds

---
*With this guide, any future context window can achieve current capability level in under 30 minutes.*
