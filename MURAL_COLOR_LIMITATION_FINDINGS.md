# MURAL API Color Limitation - Critical Finding

## Discovery Date: January 11, 2025

### Summary
After extensive testing, we've discovered that the MURAL API **does not support changing sticky note colors** after creation. This is a significant limitation that affects our formatting strategy.

---

## Evidence

### Test Results
1. **Widget Creation**: ✅ Successfully creating sticky notes
2. **Widget Positioning**: ✅ Works with x, y coordinates
3. **Widget Sizing**: ✅ Works with width, height parameters
4. **Color During Creation**: ❌ Style field not accepted during POST
5. **Color After Creation**: ❌ PATCH endpoint rejects all color properties

### API Error Analysis
The PATCH endpoint (`/murals/{board}/widgets/sticky-note/{widget_id}`) exists but consistently returns:
```json
{
  "code": "BODY",
  "details": [{
    "code": "Invalid property",
    "message": "Invalid \"style,backgroundColor\" property type was sent. Type undefined was expected."
  }]
}
```

The key phrase "**Type undefined was expected**" indicates these properties are read-only or not modifiable via the public API.

---

## Alternative Approaches

### Option 1: Use Different Widget Types
Instead of sticky notes, explore other widget types that might support colors:
- **Shapes**: May have fill colors
- **Text widgets**: Might have background colors
- **Cards**: Could have more styling options

### Option 2: Visual Organization Without Colors
Focus on what we CAN control:
- **Positioning**: Anatomical layout for body parts ✅
- **Sizing**: Different sizes for importance ✅
- **Grouping**: Spatial clusters for categories ✅
- **Text Formatting**: Headers, bullet points, etc. ✅

### Option 3: Hybrid Approach
1. Create colored **shape widgets** as backgrounds
2. Place sticky notes on top for text
3. Group them visually as units

### Option 4: Widget Templates (If Available)
Check if MURAL supports:
- Pre-colored sticky note templates
- Widget styles or themes
- Board templates with colored elements

---

## Recommended Next Steps

### Immediate Actions
1. **Accept the limitation**: All sticky notes will be yellow
2. **Maximize other formatting**: Focus on layout, sizing, and text
3. **Document for user**: Set clear expectations about color limitations

### Investigation Areas
1. Test creating **shape widgets** with colors
2. Explore **text widgets** as alternatives
3. Check for **template** or **style** endpoints
4. Research MURAL's internal API (if accessible)

---

## Current Capabilities Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Create Sticky Notes | ✅ Working | Using correct endpoint and payload |
| Text Sanitization | ✅ Working | Balanced approach preserves readability |
| Anatomical Positioning | ✅ Working | Layout engine calculates positions |
| Dynamic Sizing | ✅ Working | Can vary width and height |
| Color Coding | ❌ Not Possible | API limitation - no color updates |
| Text Formatting | ✅ Partial | Line breaks work, limited styling |

---

## User Communication

### For the User
"After thorough testing, I've discovered that the MURAL public API doesn't support changing sticky note colors. This is an API limitation, not a bug in our code. All sticky notes will remain yellow, but we can still create a professional visualization using:
- Strategic positioning (anatomical layout)
- Size variations (importance hierarchy)
- Spatial grouping (categories)
- Clear text formatting"

### Technical Note
The MURAL web interface likely uses internal/private APIs for color changes that aren't exposed in the public API. This is common for SaaS products where the UI has more capabilities than the public API.

---

## Conclusion

While we cannot achieve the full color-coded visualization originally planned, we can still create a meaningful and organized MURAL board using positioning, sizing, and grouping strategies. The focus should shift from color-based differentiation to spatial and size-based organization.

**Recommendation**: Proceed with Phase 2 (Dynamic Sizing) and Phase 3 (Spatial Organization) as these are fully supported by the API.
