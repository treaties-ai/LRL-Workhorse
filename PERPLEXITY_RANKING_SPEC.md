# Perplexity Thread Analysis & Source Ranking Specification
## Processing Licia's 20 Existing Research Threads

### 📌 Critical Understanding
**Licia has ALREADY created 20 Perplexity research threads in the browser**
- These are existing threads, not to be generated
- Each thread contains 25-30 sources (500-600 total sources)
- Licia's concern: "Often half to two-thirds are just some random person on a website"
- Task: Analyze, rank, and synthesize her existing research

---

## 🎯 Source Ranking System

### Tier 1: Academic Gold Standard (Score 24-30/30)
**Characteristics:**
- Peer-reviewed journals
- University research publications
- Systematic reviews and meta-analyses
- Clinical trials and studies
- High citation count
- Recent publication (last 5 years preferred)

**Marking:** ⭐ **GOLD STANDARD**

**Weight in Synthesis:** 3x

**Examples:**
- Nature, Science, JAMA, Lancet
- Journal of Traumatic Stress
- Clinical Psychology Review
- Neuroscience & Biobehavioral Reviews

### Tier 2: Professional & Expert (Score 15-23/30)
**Characteristics:**
- Professional publications
- Expert practitioners with credentials
- Industry standards and guidelines
- Books by recognized authorities
- Reputable organizations
- Clinical experience reports

**Marking:** ✓ **RELIABLE**

**Weight in Synthesis:** 2x

**Examples:**
- Harvard Health Publishing
- APA resources
- Books by established experts
- Professional association guidelines
- Government health resources

### Tier 3: General Web Content (Score 0-14/30)
**Characteristics:**
- Blog posts
- Personal opinions
- Unverified claims
- Anecdotal evidence
- Forum discussions
- Commercial websites

**Marking:** ⚠️ **USE WITH CAUTION**

**Weight in Synthesis:** 1x

**Examples:**
- Personal blogs
- Reddit threads
- Commercial wellness sites
- Unattributed web articles

---

## 📊 Scoring Matrix

### Academic Credibility (0-10 points)
- Peer-reviewed journal: +3
- University affiliation: +2
- Author credentials (PhD, MD, etc.): +2
- Citation metrics: +2
- Publication reputation: +1

### Research Depth (0-10 points)
- Primary research: +3
- Systematic review/meta-analysis: +3
- Clinical study: +2
- Expert commentary with citations: +1
- Opinion without citations: 0

### Methodological Rigor (0-10 points)
- Clear methodology: +3
- Adequate sample size: +2
- Control groups/conditions: +2
- Limitations acknowledged: +2
- Replicable: +1

**Total Score: 0-30 points**

---

## 🔄 Processing Workflow

### Phase 1: Thread Intake
```yaml
for each of 20 threads:
  1. Extract thread title/topic
  2. Capture Licia's original questions
  3. Extract all 25-30 source URLs
  4. Preserve source context (why cited)
  5. Note thread creation date
```

### Phase 2: Source Analysis
```yaml
for each source:
  1. Identify source type
  2. Extract author credentials
  3. Check publication venue
  4. Assess methodology (if research)
  5. Calculate quality score (0-30)
  6. Assign tier (1, 2, or 3)
  7. Flag potential issues
```

### Phase 3: Quality Synthesis
```yaml
for each thread:
  1. Create tier breakdown:
     - X% Tier 1 (Academic)
     - Y% Tier 2 (Professional)
     - Z% Tier 3 (General)
  
  2. Weight insights by source quality
  
  3. Flag unsupported claims:
     - 🚨 "Needs better source" (only Tier 3 support)
     - ✅ "Well-supported" (multiple Tier 1 sources)
     - 📊 "Mixed evidence" (conflicting tiers)
```

### Phase 4: Question Extraction
```yaml
for each thread:
  1. Extract Licia's driving questions
  2. Identify sub-questions explored
  3. Note which questions got answered
  4. Flag questions needing more research
  5. Map questions to book chapters
```

### Phase 5: Clustering & Flow
```yaml
across all threads:
  1. Identify overlapping questions
  2. Cluster by theme
  3. Create narrative sequences
  4. Map to potential chapters
  5. Show connection patterns
```

---

## 📝 Output Format

### Per-Thread Analysis Report
```markdown
# Thread: [Title]
## Topic: [Main subject]
## Date: [When created]

### Source Quality Breakdown
- Tier 1 (Academic): X sources (X%)
- Tier 2 (Professional): Y sources (Y%)  
- Tier 3 (General): Z sources (Z%)

### Key Findings by Source Tier
#### From Gold Standard Sources:
- [Finding with source reference]

#### From Professional Sources:
- [Finding with source reference]

#### From General Sources (Use Cautiously):
- [Finding with source reference]

### Questions Explored
1. [Primary question]
   - Answer quality: [Well-supported/Mixed/Weak]
2. [Secondary questions...]

### Gaps Identified
- [Topics needing better sources]
- [Unanswered questions]

### Connection to Other Threads
- Overlaps with: [Thread names]
- Shared themes: [Themes]
```

### Master Synthesis Document
```markdown
# Perplexity Research Synthesis
## Analysis of 20 Threads (500-600 sources)

### Overall Source Quality
- Average thread quality score: X/30
- Total Tier 1 sources: X (X%)
- Total Tier 2 sources: Y (Y%)
- Total Tier 3 sources: Z (Z%)

### Strongest Evidence Areas
[Topics with multiple Tier 1 sources]

### Weakest Evidence Areas
[Topics relying on Tier 3 sources]

### Question Clusters for Chapters
[Organized by theme with flow]

### Research Gaps
[What needs additional investigation]

### Recommendations
[Priority areas for additional research]
```

---

## 🚨 Special Considerations

### For Licia's Method
- She guides explorations first, then finds science
- Looking for science "Bessel wouldn't think to look for"
- Multi-directional: practice ↔ science
- Open-ended pattern discovery

### Quality Flags
- 🏆 **Breakthrough Finding**: Tier 1 source with novel insight
- 🔬 **Needs Validation**: Interesting Tier 3 claim needing research
- ⚡ **Convergent Evidence**: Multiple tiers pointing same direction
- ❓ **Contradictory Evidence**: Sources disagree
- 🌟 **Licia's Innovation**: Her insight beyond all sources

### Bridge to Bessel
- Identify Tier 1 sources that support Licia's approach
- Find research that bridges their perspectives
- Note where science validates somatic wisdom

---

## 💡 For Editorial Sprint

### Deliverables
1. **Source Quality Dashboard**: Visual breakdown of research quality
2. **Question Flow Map**: How questions connect and cluster
3. **Evidence Strength Indicators**: What's well-supported vs. speculative
4. **Gap Analysis**: Where more research is needed
5. **Chapter Alignment**: How research maps to book structure

### Presentation Format
- Modular cards for each thread
- Color-coded by source quality
- Sticky note summaries
- Whiteboard-friendly visuals
- Connection lines between themes

---

## 🎬 Implementation Steps

### When Threads Arrive:
1. Create intake template
2. Process first thread as test
3. Refine scoring based on actual sources
4. Batch process remaining threads
5. Generate synthesis reports
6. Create editorial materials

### Time Estimate:
- Per thread analysis: 20-30 minutes
- Total processing: 8-10 hours
- Synthesis generation: 2 hours
- Editorial materials: 2 hours
- **Total: 12-14 hours**

---

## 📊 Success Metrics

1. **All 500-600 sources categorized and scored**
2. **Clear quality indicators throughout**
3. **Questions clustered with narrative flow**
4. **Gaps and opportunities identified**
5. **Editorial team has actionable insights**
6. **Bessel can see the scientific rigor**
7. **Licia's wisdom properly contextualized**

---

*"It spit out all kinds of studies that I don't think it would occur to Bessel to look at." - Licia Sky*

This ranking system ensures we separate the wheat from the chaff while honoring Licia's innovative research approach.
