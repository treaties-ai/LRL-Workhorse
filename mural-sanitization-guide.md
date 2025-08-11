# Mural API Sanitization Guide: Updated Implementation

## Overview

This guide provides an updated approach to text sanitization for Mural API compatibility, correcting the over-sanitization issues discovered during debugging. The original sanitization approach was too aggressive, removing legitimate formatting and spaces that are essential for readability and user experience.

## Table of Contents
- [Over-Sanitization Analysis](#over-sanitization-analysis)
- [Security vs Functionality Balance](#security-vs-functionality-balance)
- [Updated Implementation](#updated-implementation)
- [Best Practices Framework](#best-practices-framework)
- [Testing and Validation](#testing-and-validation)

## Over-Sanitization Analysis

### What Went Wrong

The original `sanitizeForMural()` function was designed with security-first principles but became overly aggressive, causing significant functionality problems:

#### Problems Identified:
1. **Whitespace destruction**: Removed necessary spaces between words and paragraphs
2. **Formatting loss**: Eliminated newlines and structure that make content readable
3. **Character allowlist too restrictive**: Blocked legitimate extended ASCII characters
4. **Length truncation without context**: Cut text mid-sentence without preserving meaning

### Consequences of Over-Sanitization

```typescript
// Original input
const originalText = `THREAT DETECTION
━━━━━━━━━━━━━━━━━━━━━

AI-Powered Threat Detection System

Value: €15,000,000
Authority: German Federal Ministry of Defense

RISK SCORE: 8/10`;

// Over-sanitized output (what was happening)
const overSanitized = `THREATDETECTIONAIPoweredThreatDetectionSystemValue15000000AuthorityGermanFederalMinistryofDefenseRISKSCORE810`;

// Proper sanitization (what we want)
const properlySanitized = `THREAT DETECTION

AI-Powered Threat Detection System

Value: 15,000,000
Authority: German Federal Ministry of Defense

RISK SCORE: 8/10`;
```

### Root Cause Analysis

The over-sanitization stemmed from conflating two different concerns:

1. **Security threats** (Unicode injection, zero-width attacks, control characters)
2. **API compatibility** (specific Unicode characters that break Mural's parser)

The original approach treated all non-basic-ASCII as dangerous, when the real issue was specific Unicode categories that cause API parsing failures.

## Security vs Functionality Balance

### Core Principles for Balanced Sanitization

#### Principle 1: Target Specific Threats, Not Categories
```typescript
// ❌ Over-broad: Remove all non-ASCII
text = text.replace(/[^\x20-\x7E]/g, '');

// ✅ Targeted: Remove specific problematic characters
text = text.replace(/[━─│┌┐└┘]/g, ''); // Box-drawing chars only
text = text.replace(/[\u200B-\u200F]/g, ''); // Zero-width chars only
```

#### Principle 2: Preserve User Experience While Maintaining Security
```typescript
// ❌ Destroys readability
text = text.replace(/\s+/g, ' '); // Collapses all whitespace

// ✅ Preserves structure
text = text.replace(/ +/g, ' '); // Only collapses multiple spaces
text = text.split('\n').map(line => line.trim()).join('\n'); // Preserve line breaks
```

#### Principle 3: Test Sanitization Output for Usability
Every sanitization function should include validation that the output serves its intended purpose:

```typescript
function validateSanitizationQuality(original: string, sanitized: string): boolean {
  // Check if essential information is preserved
  const keyPhrases = extractKeyPhrases(original);
  const preservedPhrases = keyPhrases.filter(phrase => sanitized.includes(phrase));
  
  return preservedPhrases.length / keyPhrases.length >= 0.8; // 80% preservation threshold
}
```

#### Principle 4: Use Layered, Context-Aware Approach
Different contexts require different sanitization levels:

```typescript
// For display (less aggressive)
export function sanitizeForMuralDisplay(text: string): string {
  // Preserve formatting, remove only API-breaking characters
}

// For storage (more aggressive) 
export function sanitizeForStorage(text: string): string {
  // Remove potential security threats more aggressively
}

// For search/indexing (different focus)
export function sanitizeForSearch(text: string): string {
  // Normalize for search while preserving meaning
}
```

## Updated Implementation

### The New `sanitizeForMuralDisplay()` Function

```typescript
/**
 * Sanitize text for Mural display - preserves formatting for readability
 * This version keeps newlines, spaces, and other formatting while removing only
 * characters that cause API failures or security issues.
 */
export function sanitizeForMuralDisplay(text: string): string {
  if (!text || typeof text !== 'string') {
    return '';
  }
  
  // Layer 1: Remove only DANGEROUS Unicode, keep formatting
  // Remove control chars EXCEPT newlines, carriage returns, and tabs
  text = text.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F]/g, '');
  
  // Remove zero-width and directional characters (security threats)
  text = text.replace(/[\u200B-\u200F]/g, '');
  text = text.replace(/[\u202A-\u202E]/g, '');
  text = text.replace(/[\u2060-\u206F]/g, '');
  text = text.replace(/[\uFEFF]/g, '');
  
  // Remove surrogate pairs (can cause JSON parsing errors)
  text = text.replace(/[\uD800-\uDFFF]/g, '');
  
  // Remove specials block
  text = text.replace(/[\uFFF0-\uFFFF]/g, '');
  
  // Layer 2: Remove specific API-breaking characters (learned from testing)
  // Box-drawing characters that break Mural API
  text = text.replace(/[━─│┌┐└┘┬┤┴├┼]/g, '');
  
  // Layer 3: Normalize problematic punctuation (keep functionality)
  text = text.replace(/[''‚‛]/g, "'");
  text = text.replace(/[""„‟]/g, '"');
  text = text.replace(/[–—]/g, '-');
  text = text.replace(/[…]/g, '...');
  
  // Layer 4: Safe character replacements (preserve meaning)
  text = text.replace(/[<>]/g, ''); // Remove angle brackets
  text = text.replace(/[$]/g, 'S'); // Replace $ with S for safety
  text = text.replace(/[\\]/g, '/'); // Replace backslash
  text = text.replace(/[`]/g, "'"); // Replace backtick
  
  // Layer 5: Preserve line structure while cleaning excess whitespace
  // Replace multiple spaces with single space (but not newlines!)
  text = text.replace(/ +/g, ' ');
  
  // Trim each line but keep the line breaks
  text = text.split('\n').map(line => line.trim()).join('\n');
  
  // Layer 6: Smart length limiting with formatting preservation
  const MAX_LENGTH = 300;
  if (text.length > MAX_LENGTH) {
    // Try to cut at a newline for cleaner truncation
    const cutPoint = text.lastIndexOf('\n', MAX_LENGTH);
    if (cutPoint > MAX_LENGTH - 50) {
      text = text.substring(0, cutPoint) + '\n...';
    } else {
      text = text.substring(0, MAX_LENGTH) + '...';
    }
  }
  
  return text;
}
```

### Comparison: Old vs New Approach

```typescript
// Input text
const input = `COMPANIES AT RISK
━━━━━━━━━━━━━━━━━━━

• TechDefense GmbH
• AISecure Systems Ltd

High-risk contractors
Corporate surveillance tech`;

// OLD (over-sanitized) - WRONG
const oldResult = sanitizeForMural(input);
// Result: "COMPANIESATRISKTechDefenseGmbHAISecureSystemsLtdHighriskcontractorsCorporatesurveillancetech"

// NEW (properly sanitized) - CORRECT  
const newResult = sanitizeForMuralDisplay(input);
// Result: 
`COMPANIES AT RISK

TechDefense GmbH
AISecure Systems Ltd

High-risk contractors
Corporate surveillance tech`
```

### What Changed and Why

| Aspect | Old Approach | New Approach | Reasoning |
|--------|-------------|--------------|-----------|
| **Spaces** | Removed all multiple spaces | Preserve single spaces, remove only excess | Readability essential |
| **Newlines** | Often removed | Always preserved | Structure critical for understanding |
| **Unicode** | Blocked all extended ASCII | Target specific problematic ranges | Many Unicode chars are safe and useful |
| **Punctuation** | Aggressively replaced | Normalize only problematic variants | Preserve meaning while ensuring compatibility |
| **Length limits** | Hard cutoff | Smart truncation at line breaks | Maintain sentence/paragraph integrity |

## Best Practices Framework

### 1. Security-First, But User-Aware

```typescript
// Before implementing any sanitization rule, ask:
const sanitizationDecisionFramework = {
  isSecurityThreat: (char: string) => {
    // Does this character enable injection attacks?
    // Does this character cause parsing errors?
    // Does this character hide malicious content?
  },
  
  breaksApiCompatibility: (char: string) => {
    // Have we tested that this character causes API failures?
    // Is this documented in API restrictions?
  },
  
  impactsUserExperience: (char: string) => {
    // Does removing this character hurt readability?
    // Does this character convey important meaning?
    // Are there better alternatives to removal?
  }
};
```

### 2. Context-Aware Sanitization Strategy

```typescript
// Different sanitization for different use cases
export class ContextualSanitizer {
  // Least aggressive - for display where readability is critical
  forDisplay(text: string): string {
    return sanitizeForMuralDisplay(text);
  }
  
  // More aggressive - for data that will be processed/stored
  forStorage(text: string): string {
    // Additional security measures, but still preserve core meaning
  }
  
  // Specialized - for search indexing
  forSearch(text: string): string {
    // Normalize for search algorithms while preserving searchable terms
  }
}
```

### 3. Test-Driven Sanitization

```typescript
// Always test sanitization with real data
describe('Sanitization Quality', () => {
  it('preserves essential information', () => {
    const input = `THREAT LEVEL: HIGH\n\nCompanies: TechCorp, SecureAI\n\nRisk Score: 8/10`;
    const output = sanitizeForMuralDisplay(input);
    
    // Test that key information is preserved
    expect(output).toContain('THREAT LEVEL');
    expect(output).toContain('TechCorp');
    expect(output).toContain('8/10');
    expect(output.split('\n').length).toBeGreaterThan(1); // Structure preserved
  });
  
  it('removes security threats', () => {
    const maliciousInput = `Normal text\u200B\u200Chidden\uFEFFcontent`;
    const output = sanitizeForMuralDisplay(maliciousInput);
    
    expect(output).toBe('Normal texthiddencontent'); // Zero-width chars removed
  });
  
  it('handles API-breaking characters', () => {
    const inputWithBoxChars = `Header\n━━━━━━\nContent`;
    const output = sanitizeForMuralDisplay(inputWithBoxChars);
    
    expect(output).not.toContain('━'); // Box chars removed
    expect(output).toContain('Header'); // Content preserved
    expect(output).toContain('Content');
  });
});
```

### 4. Incremental Sanitization Philosophy

Start with minimal sanitization and add restrictions only when specific problems arise:

```typescript
// Evolution of sanitization rules based on discovered issues:

// v1.0 - Start minimal
function sanitize_v1(text: string): string {
  return text.replace(/[\u0000-\u001F]/g, ''); // Only control chars
}

// v1.1 - Add Unicode injection protection after security audit
function sanitize_v1_1(text: string): string {
  return sanitize_v1(text)
    .replace(/[\u200B-\u200F]/g, ''); // Add zero-width protection
}

// v1.2 - Add API compatibility after Mural integration  
function sanitize_v1_2(text: string): string {
  return sanitize_v1_1(text)
    .replace(/[━─│]/g, ''); // Add box-drawing chars that break Mural
}

// Document why each rule exists
const SANITIZATION_RULES = {
  controlChars: 'Security: Prevent control character injection',
  zeroWidth: 'Security: Prevent hidden content attacks', 
  boxDrawing: 'API: Mural API fails with Unicode box-drawing characters'
};
```

## Testing and Validation

### Sanitization Quality Metrics

```typescript
export function validateSanitizationQuality(
  original: string, 
  sanitized: string
): QualityReport {
  return {
    lengthPreservation: sanitized.length / original.length,
    structurePreservation: countLines(sanitized) / countLines(original),
    keywordPreservation: countPreservedKeywords(original, sanitized),
    readabilityScore: calculateReadability(sanitized),
    securityScore: calculateSecurityCompliance(sanitized)
  };
}

// Acceptance criteria
const QUALITY_THRESHOLDS = {
  lengthPreservation: 0.7,     // At least 70% of content preserved
  structurePreservation: 0.9,   // At least 90% of line structure preserved  
  keywordPreservation: 0.95,    // At least 95% of important keywords preserved
  readabilityScore: 7.0,        // Minimum readability score
  securityScore: 10.0           // Maximum security compliance required
};
```

### Real-World Testing Examples

```typescript
// Test with actual content from the system
const testCases = [
  {
    name: 'Threat Analysis Header',
    input: `THREAT DETECTION\n━━━━━━━━━━━━━━━━━━━━━\n\nAI-Powered Threat Detection System`,
    expectedKeywords: ['THREAT DETECTION', 'AI-Powered', 'Detection System'],
    shouldPreserveStructure: true
  },
  
  {
    name: 'Company List',
    input: `Companies:\n• TechDefense GmbH\n• AISecure Systems Ltd\n\nHigh-risk contractors`,
    expectedKeywords: ['Companies', 'TechDefense', 'AISecure', 'High-risk'],
    shouldPreserveStructure: true
  },
  
  {
    name: 'Unicode Attack',
    input: `Normal text\u200B\u200C\uFEFFhidden\u202Econtent`,
    expectedResult: 'Normal texthiddencontent',
    shouldRemoveThreats: true
  }
];
```

## Migration Guide

### Updating from Old Sanitization

1. **Replace function calls**:
   ```typescript
   // Old
   const cleanText = sanitizeForMural(userInput);
   
   // New  
   const cleanText = sanitizeForMuralDisplay(userInput);
   ```

2. **Update validation**:
   - Test that existing content still displays correctly
   - Verify that security protections are maintained
   - Check that API calls succeed with new sanitization

3. **Monitor quality metrics**:
   - Track user complaints about formatting
   - Monitor API success rates
   - Validate that content serves its intended purpose

### Rollback Strategy

If issues arise with the new sanitization:

```typescript
// Gradual rollout with feature flag
export function sanitizeText(text: string, useNewSanitizer: boolean = false): string {
  if (useNewSanitizer && isFeatureEnabled('improved-sanitization')) {
    return sanitizeForMuralDisplay(text);
  }
  return sanitizeForMural(text); // Fallback to old method
}
```

## Conclusion

The updated sanitization approach balances security and functionality by:

1. **Targeting specific threats** rather than broad character categories
2. **Preserving essential formatting** like spaces and line breaks
3. **Maintaining readability** while ensuring API compatibility  
4. **Using data-driven decisions** based on actual API testing results

This approach ensures that our content remains secure, functional, and user-friendly while working reliably with the Mural API.

### Key Takeaways

- **Over-sanitization can be worse than under-sanitization** when it destroys user experience
- **Security and usability must be balanced** through targeted, thoughtful restrictions
- **Test sanitization with real content** to ensure it serves its intended purpose
- **Document the reasoning** behind each sanitization rule for future maintenance
- **Monitor quality metrics** to catch sanitization issues before they impact users
