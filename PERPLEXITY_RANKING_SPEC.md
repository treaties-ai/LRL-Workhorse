# Perplexity Source Ranking & Analysis Specification
## Detailed Implementation Guide for Research Quality Assessment

**Purpose:** Transform Perplexity's 25-30 mixed-quality sources into a tiered, weighted analysis that Licia and Bessel can trust.

**Critical Context:** "Often half to two-thirds are just random people talking on websites" - We need to separate gold from noise.

---

## 🎯 Core Algorithm

### Source Quality Score Formula

```python
def calculate_source_score(source):
    """
    Calculate a 0-30 quality score for each source
    
    Components:
    - Academic Credibility (0-10)
    - Research Depth (0-10) 
    - Methodological Rigor (0-10)
    """
    
    academic_score = 0
    depth_score = 0
    rigor_score = 0
    
    # Academic Credibility Scoring
    if is_peer_reviewed(source):
        academic_score += 3
    if has_university_affiliation(source):
        academic_score += 2
    if has_professional_credentials(source.author):
        academic_score += 2
    if has_high_citations(source):
        academic_score += 2
    if from_reputable_publication(source):
        academic_score += 1
    
    # Research Depth Scoring
    if is_primary_research(source):
        depth_score += 3
    elif is_systematic_review(source):
        depth_score += 3
    elif is_clinical_study(source):
        depth_score += 2
    elif is_expert_commentary(source):
        depth_score += 1
    # Blog/opinion gets 0
    
    # Additional depth factors
    if has_large_sample_size(source):
        depth_score += 2
    if is_longitudinal_study(source):
        depth_score += 2
    if has_multiple_data_sources(source):
        depth_score += 1
    
    # Methodological Rigor Scoring
    if has_clear_methodology(source):
        rigor_score += 3
    if has_adequate_sample_size(source):
        rigor_score += 2
    if has_control_groups(source):
        rigor_score += 2
    if acknowledges_limitations(source):
        rigor_score += 2
    if is_replicable(source):
        rigor_score += 1
    
    total_score = academic_score + depth_score + rigor_score
    
    return {
        'total': total_score,
        'academic': academic_score,
        'depth': depth_score,
        'rigor': rigor_score,
        'tier': assign_tier(total_score)
    }
```

---

## 📊 Tier Classification System

### Tier 1: Academic Gold Standard (Score 24-30)
```yaml
characteristics:
  - Peer-reviewed journal articles
  - Systematic reviews and meta-analyses
  - Large-scale clinical trials
  - Seminal works by field leaders
  
visual_marker: "⭐ GOLD STANDARD"
weight_multiplier: 3x
trust_level: "Highest - cite with confidence"

examples:
  - Nature, Science, JAMA publications
  - Cochrane Reviews
  - NIH-funded studies
  - Books by recognized experts (van der Kolk, Porges, etc.)
```

### Tier 2: Professional Reliable (Score 15-23)
```yaml
characteristics:
  - Professional publications
  - Expert practitioner articles
  - Industry white papers
  - Clinical case studies
  - Reputable news outlets (health sections)
  
visual_marker: "✓ RELIABLE"
weight_multiplier: 2x
trust_level: "Good - use with context"

examples:
  - Psychology Today (expert contributors)
  - Harvard Health Publishing
  - APA publications
  - Professional association guidelines
```

### Tier 3: General Web Content (Score 0-14)
```yaml
characteristics:
  - Personal blogs
  - Opinion pieces
  - Anecdotal reports
  - Social media posts
  - Unverified claims
  
visual_marker: "⚠️ USE WITH CAUTION"
weight_multiplier: 1x
trust_level: "Low - verify independently"

examples:
  - Medium articles (non-expert)
  - Reddit discussions
  - Personal wellness blogs
  - YouTube comments
```

---

## 🔍 Source Metadata Extraction

### Required Fields to Capture

```yaml
metadata_schema:
  url: string
  title: string
  
  author:
    name: string
    credentials: array[string]
    affiliation: string
    h_index: number (optional)
    
  publication:
    venue: string
    type: enum[journal, book, website, blog, news]
    impact_factor: number (optional)
    publisher: string
    date: date
    
  research_type:
    category: enum[empirical, review, opinion, news]
    methodology: string (optional)
    sample_size: number (optional)
    
  citations:
    count: number
    recent_citations: number (last 2 years)
    
  relevance:
    to_trauma_healing: score(0-10)
    to_somatic_therapy: score(0-10)
    to_book_themes: score(0-10)
```

---

## 🎨 Visual Output Format

### Individual Source Card
```
┌─────────────────────────────────────────────┐
│ ⭐ GOLD STANDARD                            │
│                                             │
│ Title: The Polyvagal Theory: Neurophysio.. │
│ Author: Stephen W. Porges, PhD              │
│ Venue: Biological Psychology                │
│ Year: 2007 | Citations: 5,420              │
│                                             │
│ Scores: Academic: 9 | Depth: 10 | Rigor: 9 │
│ Total: 28/30                                │
│                                             │
│ Key Finding: "Vagal tone directly           │
│ correlates with emotional regulation..."    │
└─────────────────────────────────────────────┘
```

### Thread Summary Report
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERPLEXITY THREAD ANALYSIS: Somatic Interventions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE QUALITY BREAKDOWN:
⭐ Tier 1 (Gold):     8 sources (32%)
✓  Tier 2 (Reliable): 7 sources (28%)
⚠️  Tier 3 (Caution): 10 sources (40%)

TOP INSIGHTS (from Gold sources only):
• Somatic experiencing shows 85% efficacy in single-trauma PTSD
• Vagal tone improvement correlates with symptom reduction
• Cultural variations exist in somatic expression of trauma

CLAIMS NEEDING BETTER SUPPORT:
🚨 "Energy healing resolves trauma" - only Tier 3 support
🚨 "All trauma is stored in the fascia" - mixed evidence

RECOMMENDED ADDITIONAL RESEARCH:
→ Longitudinal studies on somatic intervention outcomes
→ Cross-cultural somatic therapy effectiveness
→ Neurobiological mechanisms of body-based healing
```

---

## 💻 Implementation Pipeline

### Step-by-Step Processing

```yaml
pipeline:
  1_thread_ingestion:
    input: Raw Perplexity thread HTML/JSON
    process:
      - Extract main synthesis text
      - Extract all source URLs
      - Preserve citation contexts
    output: Structured thread object
    
  2_source_fetching:
    input: List of source URLs
    process:
      - Fetch metadata via APIs (CrossRef, PubMed, Google Scholar)
      - Extract author information
      - Get citation counts
      - Identify publication venue
    output: Enriched source metadata
    
  3_scoring_engine:
    input: Enriched source metadata
    process:
      - Apply scoring algorithm
      - Calculate component scores
      - Assign tier classification
    output: Scored source list
    
  4_synthesis_weighting:
    input: Original synthesis + scored sources
    process:
      - Parse claims in synthesis
      - Map claims to supporting sources
      - Apply tier-based weights
      - Flag unsupported claims
    output: Weighted synthesis
    
  5_report_generation:
    input: All processed data
    process:
      - Create visual source cards
      - Generate quality breakdown
      - Extract key insights by tier
      - Identify research gaps
    output: Complete analysis report
```

---

## 🔧 Integration with Existing Systems

### Agent Coordination

```yaml
agent_responsibilities:
  
  Theoretical_Framework_Agent:
    - Assess academic credibility
    - Verify theoretical alignment
    - Check citation networks
    
  Clinical_Application_Agent:
    - Evaluate practical relevance
    - Assess clinical validity
    - Check for contraindications
    
  Publication_Generation_Agent:
    - Determine book relevance
    - Extract quotable passages
    - Format for editorial use
    
  Cultural_Context_Agent:
    - Check cultural sensitivity
    - Flag Western-centric bias
    - Ensure diverse perspectives
```

### ChromaDB Storage Schema

```python
collection_schema = {
    'name': 'perplexity_sources',
    'metadata': {
        'thread_id': 'string',
        'source_url': 'string',
        'tier': 'int',
        'total_score': 'float',
        'academic_score': 'float',
        'depth_score': 'float',
        'rigor_score': 'float',
        'author': 'string',
        'publication': 'string',
        'year': 'int',
        'citations': 'int'
    },
    'embedding_fields': ['title', 'abstract', 'key_findings']
}
```

---

## 📈 Quality Metrics

### Success Indicators

```yaml
quality_metrics:
  
  coverage:
    target: 100% of sources classified
    measurement: count(classified) / count(total)
    
  accuracy:
    target: 95% tier assignments validated
    measurement: manual spot checks
    
  utility:
    target: Editorial team uses rankings
    measurement: Usage tracking
    
  trust:
    target: Licia confident in rankings
    measurement: Feedback surveys
    
  improvement:
    target: Higher % Tier 1 over time
    measurement: Tier distribution trends
```

### Validation Protocol

```yaml
validation_steps:
  
  1_sample_validation:
    - Manually score 10 sources
    - Compare with algorithm scores
    - Adjust weights if needed
    
  2_expert_review:
    - Have domain expert review tier assignments
    - Get feedback on edge cases
    - Refine classification rules
    
  3_user_testing:
    - Present to Licia and team
    - Gather usability feedback
    - Iterate on visual design
    
  4_continuous_improvement:
    - Track disagreements
    - Update scoring factors
    - Expand metadata sources
```

---

## 🚀 Quick Start Guide

### For Immediate Use

```python
# Example usage for processing a single Perplexity thread

from perplexity_ranker import PerplexitySourceRanker

# Initialize ranker
ranker = PerplexitySourceRanker()

# Load thread
thread = ranker.load_thread("perplexity_thread.json")

# Process all sources
ranked_sources = ranker.rank_sources(thread.sources)

# Generate report
report = ranker.generate_report(
    thread=thread,
    sources=ranked_sources,
    include_visuals=True,
    highlight_gaps=True
)

# Save for editorial team
report.save("editorial_materials/thread_analysis.pdf")

# Extract gold-standard insights
gold_insights = report.get_tier_1_insights()
```

---

## 🔄 Continuous Improvement

### Feedback Loop

```yaml
improvement_cycle:
  
  weekly:
    - Review tier distribution
    - Check for classification errors
    - Update publication venue list
    
  monthly:
    - Analyze user feedback
    - Refine scoring weights
    - Add new metadata sources
    
  quarterly:
    - Major algorithm updates
    - Expand factor considerations
    - Performance optimization
```

### Evolution Tracking

```yaml
metrics_to_track:
  - Average thread quality score over time
  - Percentage of Tier 1 sources found
  - User satisfaction ratings
  - Time saved in research validation
  - Number of high-quality sources discovered
```

---

## 📝 Notes for Implementation

1. **Start Simple**: Begin with basic URL pattern matching for quick wins
2. **API Priority**: CrossRef and PubMed APIs are most valuable
3. **Fallback Logic**: When metadata unavailable, use conservative scoring
4. **User Override**: Allow manual tier adjustment with reasoning
5. **Batch Processing**: Process all 20 threads together for efficiency

---

*This specification ensures that Licia can trust the research quality assessment, Bessel sees rigorous source evaluation, and the editorial team has clear, actionable intelligence about their research materials.*
