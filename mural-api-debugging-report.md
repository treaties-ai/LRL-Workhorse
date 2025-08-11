# Mural API Integration: Critical Findings and Implementation Guide

## Table of Contents
- [Executive Summary](#executive-summary)
- [Primary Issue: Text Content Complexity](#primary-issue-text-content-complexity-and-unicode-limitations)
- [API Payload Structure](#api-payload-structure-critical-requirements)
- [Bulk Creation Limits](#bulk-creation-limits-and-batch-processing)
- [Sanitization Implementation](#sanitization-and-security-implementation)
- [Error Patterns and Debugging](#error-patterns-and-debugging-strategy)
- [Architecture Validation](#architecture-validation-what-worked-correctly)
- [Production Guidelines](#calibration-guidelines-for-production-systems)

## Executive Summary

After extensive debugging of "Invalid payload" errors in our Mural API integration, we've identified the root cause and implemented a working solution. The issue was **text content complexity**, not architectural problems. Our visualization logic, coordinate calculations, and API structure were correct from the start. This report documents the critical findings, implementation patterns, and calibration guidelines for robust Mural API integration.

## Primary Issue: Text Content Complexity and Unicode Limitations

The Mural API has undocumented restrictions on text content that cause silent failures with misleading error messages. **Key finding**: Unicode box-drawing characters (━, ─, │, etc.) and overly complex text formatting cause the API to reject entire payloads with vague "Invalid payload" errors.

### Working vs. Failing Text Formats

```typescript
// ❌ FAILS - Unicode characters and complex formatting
`THREAT DETECTION
━━━━━━━━━━━━━━━━━━━━━

${title}

Value: ${value}
Authority: ${authority}

RISK SCORE: ${score}/10

Status: CRITICAL PRIORITY`

// ✅ WORKS - Simple ASCII formatting  
`THREAT DETECTION

${title}

Value: ${value}
Risk Score: ${score}/10
Status: CRITICAL`
```

### Implementation Rule
Stick to basic ASCII characters (A-Z, a-z, 0-9, basic punctuation) and simple newline formatting. Avoid Unicode decorative characters, bullets (•), arrows (→), and box-drawing characters entirely.

## API Payload Structure: Critical Requirements

The Mural sticky note creation API requires specific field structures that differ from documentation examples:

### Required Fields for Sticky Note Creation
```typescript
{
  shape: 'rectangle',    // REQUIRED - API fails without this
  text: string,          // REQUIRED - must be ASCII-safe
  x: number,            // REQUIRED - coordinate positioning  
  y: number,            // REQUIRED - coordinate positioning
  width: number,        // REQUIRED - typically 138 for standard stickies
  height: number        // REQUIRED - typically 138 for standard stickies
}
```

### Fields That Cause Failures
- `style: { backgroundColor: '#color' }` - API returns "Type undefined was expected" error
- Any nested style objects during creation (colors can only be set via PATCH updates)
- Missing `shape` field causes "Type 'circle', 'rectangle' was expected" error

## Bulk Creation Limits and Batch Processing

**Critical discovery**: The API accepts bulk creation of 20+ sticky notes when text content is simplified, but fails with complex text even for small batches.

### Tested Limits
- ✅ **1 sticky note**: Always works with any text content
- ✅ **2-5 sticky notes**: Works with simplified text  
- ✅ **10 sticky notes**: Works with very short text (under 20 chars each)
- ✅ **20 sticky notes**: Works with moderately simple text (our current implementation)
- ❌ **20+ sticky notes**: Fails with complex Unicode-heavy text

### Recommended Batch Strategy
```typescript
// Process in chunks with content validation
const MAX_BATCH_SIZE = 20;
const MAX_TEXT_LENGTH = 200; // chars per sticky

function processBatch(stickies: StickyNote[]) {
  return stickies
    .map(sticky => ({
      ...sticky,
      text: sanitizeForMuralDisplay(sticky.text) // Remove Unicode, limit length
    }))
    .slice(0, MAX_BATCH_SIZE);
}
```

## Sanitization and Security Implementation

We implemented a multi-layer sanitization system that proved critical for API compatibility:

### Layer 1 - Unicode Safety
```typescript
// Remove dangerous Unicode categories
text = text.replace(/[\u0000-\u001F\u007F-\u009F]/g, ''); // Control chars
text = text.replace(/[\u200B-\u200F]/g, ''); // Zero-width spaces  
text = text.replace(/[\uD800-\uDFFF]/g, ''); // Surrogate pairs
text = text.replace(/[━─│┌┐└┘]/g, ''); // Box-drawing chars
```

### Layer 2 - Content Validation
```typescript
// Allowlist enforcement - only safe characters
text = text.replace(/[^\x20-\x7E\u00A0-\u00FF\n\r\t]/g, '');

// Length limits (critical for API acceptance)  
const MAX_LENGTH = 300; // Adjust based on testing
if (text.length > MAX_LENGTH) {
  text = text.substring(0, MAX_LENGTH) + '...';
}
```

**Security bonus**: This sanitization also prevents Unicode injection attacks and ensures consistent display across different systems.

## Error Patterns and Debugging Strategy

The Mural API provides misleading error messages that don't directly indicate the root cause:

### Common Error Patterns
- `"Invalid payload"` + `"shape property type"` = Missing required `shape` field
- `"Invalid payload"` + `"backgroundColor property type undefined expected"` = Style field not allowed during creation
- `"Invalid payload"` with no specific field mentioned = Usually Unicode/text complexity issue
- `HTTP 400` with retry behavior = Text content causing validation failure

### Debugging Methodology That Worked
1. **Start simple**: Test with minimal payload (single sticky, short ASCII text)
2. **Incremental complexity**: Add fields one by one to isolate failures  
3. **Content isolation**: Test same structure with different text content
4. **Batch size testing**: Try 1, 2, 5, 10+ sticky notes to find limits
5. **Character analysis**: Remove special characters systematically

### Debugging Tools to Implement
```typescript
// Add comprehensive logging before API calls
console.log('DEBUG: Payload size:', JSON.stringify(payload).length, 'bytes');
console.log('DEBUG: Text lengths:', payload.map(s => s.text.length));  
console.log('DEBUG: Unicode check:', payload.some(s => /[^\x20-\x7E\n\r\t]/.test(s.text)));
```

## Architecture Validation: What Worked Correctly

**Important note**: The advanced developer's analysis was correct about our architecture quality. These components worked perfectly and should be preserved:

- ✅ **Coordinate calculation logic** (`placeRing` function with trigonometry) - mathematically sound
- ✅ **Ring-based layout system** - produces proper spacing and positioning  
- ✅ **Agent-based data synthesis** - generates appropriate structured content
- ✅ **Workflow orchestration** - `npm run visualize` executes correct pipeline
- ✅ **API client structure** - proper authentication, error handling, retry logic

### Key Lesson
Don't refactor working architectural components when troubleshooting API integration issues. The problem was content formatting, not system design.

## Calibration Guidelines for Production Systems

### Immediate Implementation Recommendations

1. **Text preprocessing pipeline**: Implement the sanitization functions as a mandatory step before any Mural API calls
2. **Content length monitoring**: Add metrics tracking text length distribution to catch content that might cause API failures  
3. **Batch size optimization**: Start with batches of 10-15 sticky notes and monitor success rates
4. **Unicode audit**: Scan existing content for problematic characters and establish content guidelines for users
5. **Error categorization**: Implement specific error handling for "Invalid payload" vs. authentication vs. rate limiting errors
6. **Fallback strategies**: If bulk creation fails, implement automatic retry with single-sticky creation as backup

### Long-term System Improvements

- **Content validation service**: Create a service that checks Mural compatibility before API calls
- **A/B testing**: Test different text complexity levels to find optimal formatting
- **Monitoring dashboards**: Build dashboards for API success rates correlated with content characteristics
- **Content guidelines**: Document approved text formatting patterns for content creators in your organization

## Conclusion

This debugging process revealed that API integration issues often stem from undocumented content restrictions rather than architectural problems. The key is systematic isolation testing combined with comprehensive logging to identify the actual constraint boundaries.

**Final success metrics:**
- ✅ **20 sticky notes created successfully** in single API call
- ✅ **Proper ring-based positioning** maintained
- ✅ **Readable, well-formatted content** preserved
- ✅ **No Unicode security vulnerabilities** introduced
- ✅ **Robust error handling** and debugging capabilities added

The system now reliably creates organized, professional Mural visualizations that serve the intended analytical and collaborative purposes.
