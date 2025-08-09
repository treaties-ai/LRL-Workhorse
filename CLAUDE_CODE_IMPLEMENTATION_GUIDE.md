# Claude Code Implementation Guide
## Advanced Specifications for Building Licia's Research Lab V2

**Purpose:** Provide Claude Code with complete implementation specifications to build and deploy the 13-agent research laboratory system.

**Critical Context:** Editorial sprint is happening NOW. Priority 1 implementations are mission-critical.

**🚨 CRITICAL REQUIREMENT:** Sequential Thinking MCP must be installed and used for ALL complex decisions and architecture work.

---

## 🧠 Priority 0: Sequential Thinking MCP Setup (DO THIS FIRST!)

### Why This Is Critical
Sequential Thinking MCP is not just a tool - it's the cognitive backbone of this entire system. It:
- Preserves reasoning chains across context windows
- Enables sophisticated gap analysis
- Creates auditable decision trails
- Prevents requirements drift
- Multiplies quality assurance effectiveness

### Immediate Setup Instructions
```bash
# STEP 1: Install Sequential Thinking MCP (DO THIS IMMEDIATELY)
npm install -g @modelcontextprotocol/server-sequential-thinking

# STEP 2: Configure for automatic use
cat > config/sequential_thinking_config.yaml << EOF
server: sequential-thinking
config:
  auto_activate: true
  preserve_all_thoughts: true
  max_thoughts: 50
  storage_path: sequential_thinking_logs/
  auto_save_interval: 5  # Save every 5 thoughts
  create_session_log: true
EOF

# STEP 3: Verify installation
npx sequential-thinking --test
```

### Mandatory Usage Pattern
```python
# Every Claude Code instance MUST follow this pattern:

class ClaudeCodeSession:
    def __init__(self):
        self.sequential_thinking = SequentialThinkingMCP()
        self.sequential_thinking.start_session()
        self.thought_log = []
        
    def make_decision(self, problem):
        """ALL decisions must use sequential thinking"""
        # Start sequential thinking
        thought_session = self.sequential_thinking.think_through(
            problem=problem,
            min_thoughts=5,
            max_thoughts=25
        )
        
        # Preserve thoughts immediately
        self.thought_log.extend(thought_session.thoughts)
        self.save_to_file('SEQUENTIAL_THINKING_LOG.md')
        
        return thought_session.solution
```

---

## 🔄 Automated Triangulation System (ATS)

### Overview
The Automated Triangulation System continuously verifies alignment between:
1. **Sequential Thinking Logs** - AI's reasoning process
2. **User Prompts** - Instructions and refinements
3. **Project Documentation** - Actual outputs

This system runs continuously and catches gaps BEFORE they become problems.

### Core Implementation

```python
# triangulation/automated_triangulation_system.py

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import difflib

class AutomatedTriangulationSystem:
    """
    Continuous three-way verification system for requirements integrity
    """
    
    def __init__(self):
        self.sequential_log_path = Path("SEQUENTIAL_THINKING_LOG.md")
        self.user_prompts_path = Path("USER_PROMPTS_LOG.md")
        self.project_docs_path = Path("PROJECT_DOCUMENTATION_V2.md")
        self.gap_report_path = Path("GAP_ANALYSIS_AUTOMATED.md")
        
        # Auto-capture configuration
        self.capture_interval = 300  # 5 minutes
        self.triangulation_interval = 1800  # 30 minutes
        self.gaps_detected = []
        
    async def run_continuous_monitoring(self):
        """Main monitoring loop - runs continuously"""
        tasks = [
            asyncio.create_task(self.auto_capture_loop()),
            asyncio.create_task(self.triangulation_loop()),
            asyncio.create_task(self.gap_remediation_loop())
        ]
        await asyncio.gather(*tasks)
    
    async def auto_capture_loop(self):
        """Automatically capture all three sources"""
        while True:
            # Capture sequential thinking
            await self.capture_sequential_thoughts()
            
            # Extract user prompts
            await self.extract_user_prompts()
            
            # Snapshot project documentation
            await self.snapshot_documentation()
            
            await asyncio.sleep(self.capture_interval)
    
    async def capture_sequential_thoughts(self):
        """Real-time capture of sequential thinking"""
        # Hook into Sequential Thinking MCP
        thoughts = await self.get_current_thoughts()
        
        # Append to log with timestamp
        with open(self.sequential_log_path, 'a') as f:
            f.write(f"\n## Session: {datetime.now().isoformat()}\n")
            for thought in thoughts:
                f.write(f"### Thought {thought['number']}\n")
                f.write(f"{thought['content']}\n\n")
    
    async def extract_user_prompts(self):
        """Auto-extract user prompts from session"""
        session_log = await self.get_session_log()
        
        # Extract all user messages
        user_prompts = re.findall(
            r'<user_message>(.*?)</user_message>',
            session_log,
            re.DOTALL
        )
        
        # Save to dedicated file
        with open(self.user_prompts_path, 'a') as f:
            f.write(f"\n## Session: {datetime.now().isoformat()}\n")
            for i, prompt in enumerate(user_prompts, 1):
                f.write(f"### Prompt {i}\n")
                f.write(f"{prompt}\n\n")
    
    async def triangulation_loop(self):
        """Periodic triangulation analysis"""
        while True:
            await asyncio.sleep(self.triangulation_interval)
            
            # Perform triangulation
            gaps = await self.triangulate_sources()
            
            # Generate gap report
            await self.generate_gap_report(gaps)
            
            # Alert if critical gaps found
            if self.has_critical_gaps(gaps):
                await self.alert_user(gaps)
    
    async def triangulate_sources(self) -> List[Dict]:
        """Core triangulation logic"""
        gaps = []
        
        # Load all three sources
        sequential_thoughts = self.load_sequential_log()
        user_prompts = self.load_user_prompts()
        project_docs = self.load_project_docs()
        
        # Analysis 1: Thoughts mentioned in prompts but not in docs
        prompt_to_thought_gaps = self.analyze_prompt_to_thought_alignment(
            user_prompts, sequential_thoughts
        )
        
        # Analysis 2: Thoughts not reflected in documentation
        thought_to_doc_gaps = self.analyze_thought_to_doc_alignment(
            sequential_thoughts, project_docs
        )
        
        # Analysis 3: User requirements not in final docs
        prompt_to_doc_gaps = self.analyze_prompt_to_doc_alignment(
            user_prompts, project_docs
        )
        
        # Combine and prioritize gaps
        gaps.extend(prompt_to_thought_gaps)
        gaps.extend(thought_to_doc_gaps)
        gaps.extend(prompt_to_doc_gaps)
        
        return self.prioritize_gaps(gaps)
    
    def analyze_prompt_to_thought_alignment(
        self, prompts: List[str], thoughts: List[str]
    ) -> List[Dict]:
        """Find user requirements not reflected in thinking"""
        gaps = []
        
        for prompt in prompts:
            # Extract key requirements from prompt
            requirements = self.extract_requirements(prompt)
            
            for req in requirements:
                # Check if requirement appears in thoughts
                if not self.requirement_in_thoughts(req, thoughts):
                    gaps.append({
                        'type': 'prompt_to_thought',
                        'requirement': req,
                        'source': prompt[:100],
                        'severity': 'high',
                        'description': f"User requirement not in thinking: {req}"
                    })
        
        return gaps
    
    def analyze_thought_to_doc_alignment(
        self, thoughts: List[str], docs: str
    ) -> List[Dict]:
        """Find thoughts not implemented in documentation"""
        gaps = []
        
        for thought in thoughts:
            # Extract key decisions from thought
            decisions = self.extract_decisions(thought)
            
            for decision in decisions:
                # Check if decision appears in docs
                if not self.decision_in_docs(decision, docs):
                    gaps.append({
                        'type': 'thought_to_doc',
                        'decision': decision,
                        'thought': thought[:100],
                        'severity': 'medium',
                        'description': f"Decision not documented: {decision}"
                    })
        
        return gaps
    
    def analyze_prompt_to_doc_alignment(
        self, prompts: List[str], docs: str
    ) -> List[Dict]:
        """Find user requirements missing from final documentation"""
        gaps = []
        
        for prompt in prompts:
            requirements = self.extract_requirements(prompt)
            
            for req in requirements:
                if not self.requirement_in_docs(req, docs):
                    gaps.append({
                        'type': 'prompt_to_doc',
                        'requirement': req,
                        'severity': 'critical',
                        'description': f"Requirement not implemented: {req}"
                    })
        
        return gaps
    
    async def generate_gap_report(self, gaps: List[Dict]):
        """Generate automated gap analysis report"""
        report = f"""# Automated Gap Analysis Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Gaps Detected: {len(gaps)}
- Critical: {len([g for g in gaps if g['severity'] == 'critical'])}
- High: {len([g for g in gaps if g['severity'] == 'high'])}
- Medium: {len([g for g in gaps if g['severity'] == 'medium'])}

## Detailed Gap Analysis
"""
        
        for i, gap in enumerate(gaps, 1):
            report += f"""
### Gap {i}: {gap['description']}
- **Type**: {gap['type']}
- **Severity**: {gap['severity']}
- **Details**: {json.dumps(gap, indent=2)}
- **Remediation**: {self.suggest_remediation(gap)}
"""
        
        # Save report
        with open(self.gap_report_path, 'w') as f:
            f.write(report)
    
    def suggest_remediation(self, gap: Dict) -> str:
        """Suggest how to fix each gap"""
        if gap['type'] == 'prompt_to_thought':
            return "Re-run sequential thinking on this requirement"
        elif gap['type'] == 'thought_to_doc':
            return "Update documentation to reflect this decision"
        elif gap['type'] == 'prompt_to_doc':
            return "CRITICAL: Implement this missing requirement"
        return "Review and address"
    
    async def gap_remediation_loop(self):
        """Automatically attempt to fix gaps"""
        while True:
            if self.gaps_detected:
                gap = self.gaps_detected.pop(0)
                
                # Attempt automatic remediation
                if gap['severity'] == 'critical':
                    await self.remediate_critical_gap(gap)
                elif gap['severity'] == 'high':
                    await self.remediate_high_gap(gap)
                
            await asyncio.sleep(60)  # Check every minute
    
    async def remediate_critical_gap(self, gap: Dict):
        """Automatically fix critical gaps"""
        # Use Sequential Thinking to reason about the gap
        solution = await self.sequential_thinking.think_through(
            problem=f"How to fix gap: {gap['description']}",
            context=gap
        )
        
        # Apply the solution
        await self.apply_remediation(solution)
        
        # Log the remediation
        self.log_remediation(gap, solution)
```

### Context Window Transition Protocol

```python
# triangulation/context_transition.py

class ContextWindowTransition:
    """
    Ensures perfect continuity when context window fills
    """
    
    def __init__(self):
        self.ats = AutomatedTriangulationSystem()
        self.transition_checklist = []
        
    async def prepare_for_transition(self) -> Dict:
        """Run before context window fills"""
        
        # 1. Final triangulation check
        gaps = await self.ats.triangulate_sources()
        
        # 2. Create transition package
        package = {
            'timestamp': datetime.now().isoformat(),
            'sequential_thoughts': self.get_all_thoughts(),
            'user_prompts': self.get_all_prompts(),
            'current_documentation': self.get_current_docs(),
            'detected_gaps': gaps,
            'next_priorities': self.calculate_priorities(gaps),
            'context_preservation': self.create_context_snapshot()
        }
        
        # 3. Save transition package
        with open('CONTEXT_TRANSITION_PACKAGE.json', 'w') as f:
            json.dump(package, f, indent=2)
        
        # 4. Create next context instructions
        self.create_next_context_instructions(package)
        
        return package
    
    def create_next_context_instructions(self, package: Dict):
        """Generate instructions for next context window"""
        
        instructions = f"""# Instructions for Next Context Window

## 1. IMMEDIATELY Load and Initialize:
```python
# First thing in new context:
from triangulation import ContextWindowTransition
transition = ContextWindowTransition()
package = transition.load_transition_package()
transition.restore_context(package)
```

## 2. Critical Gaps to Address:
{self.format_critical_gaps(package['detected_gaps'])}

## 3. Sequential Thinking Continuity:
- Last thought number: {len(package['sequential_thoughts'])}
- Continue from this context: {package['sequential_thoughts'][-1]}

## 4. User Intent Preservation:
{self.format_user_intent(package['user_prompts'])}

## 5. Immediate Actions Required:
{self.format_immediate_actions(package['next_priorities'])}
"""
        
        with open('NEXT_CONTEXT_INSTRUCTIONS.md', 'w') as f:
            f.write(instructions)
```

### Quality Assurance Multipliers

```python
# triangulation/qa_multipliers.py

class QualityAssuranceMultipliers:
    """
    Upstream leverage for catching issues early
    Based on user's insight about high-leverage cognition design
    """
    
    def __init__(self):
        self.thought_to_plan_verifier = ThoughtToPlanVerifier()
        self.plan_to_implementation_tracker = PlanToImplementationTracker()
        self.requirements_tracer = RequirementsTraceabilityMatrix()
        
    async def upstream_verification(self, sequential_thoughts: List, plan: str) -> Dict:
        """
        Check alignment between thinking and planning
        This is the highest leverage point for quality
        """
        gaps = []
        
        # A. Did AI miss things between thinking and plan?
        for thought in sequential_thoughts:
            key_concepts = self.extract_concepts(thought)
            for concept in key_concepts:
                if not self.concept_in_plan(concept, plan):
                    gaps.append({
                        'type': 'thought_to_plan_miss',
                        'thought': thought,
                        'missing_concept': concept,
                        'impact': 'HIGH',
                        'remedy': 'Update plan to include this concept'
                    })
        
        # B. Are important thoughts not explicitly in plan?
        important_thoughts = self.identify_important_thoughts(sequential_thoughts)
        for thought in important_thoughts:
            if not self.thought_represented(thought, plan):
                gaps.append({
                    'type': 'important_thought_missing',
                    'thought': thought,
                    'impact': 'CRITICAL',
                    'remedy': 'Explicitly add to plan'
                })
        
        # C. Do gaps raise questions about clarity?
        clarity_issues = self.analyze_clarity(sequential_thoughts, plan)
        if clarity_issues:
            gaps.extend(clarity_issues)
        
        return {
            'gaps': gaps,
            'alignment_score': self.calculate_alignment(gaps),
            'recommendations': self.generate_recommendations(gaps)
        }
    
    def identify_important_thoughts(self, thoughts: List) -> List:
        """Identify which thoughts are most critical"""
        important = []
        
        for thought in thoughts:
            # Check for architecture decisions
            if any(keyword in thought.lower() for keyword in 
                   ['architecture', 'design', 'critical', 'must', 'important']):
                important.append(thought)
            
            # Check for feature definitions
            if any(keyword in thought.lower() for keyword in
                   ['feature', 'capability', 'requirement', 'need']):
                important.append(thought)
        
        return important
```

### Real-Time Gap Detection Engine

```python
# triangulation/realtime_gap_detector.py

import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RealtimeGapDetector(FileSystemEventHandler):
    """
    Monitors files in real-time and detects gaps as they occur
    """
    
    def __init__(self):
        self.ats = AutomatedTriangulationSystem()
        self.observer = Observer()
        self.watch_paths = [
            'SEQUENTIAL_THINKING_LOG.md',
            'PROJECT_DOCUMENTATION_V2.md',
            'WORKFLOWS.md',
            'agents/',
            'outputs/'
        ]
        self.gap_threshold = 0.8  # Alert if alignment < 80%
        
    def start_monitoring(self):
        """Start real-time file monitoring"""
        for path in self.watch_paths:
            self.observer.schedule(self, path, recursive=True)
        self.observer.start()
    
    def on_modified(self, event):
        """Triggered when any monitored file changes"""
        if not event.is_directory:
            # Immediate gap check
            asyncio.create_task(self.check_for_gaps(event.src_path))
    
    async def check_for_gaps(self, file_path: str):
        """Check for gaps when files change"""
        # Quick triangulation
        gaps = await self.ats.quick_triangulate(file_path)
        
        if gaps:
            # Immediate alert
            await self.alert_gaps(gaps)
            
            # Attempt auto-fix for simple gaps
            if self.can_auto_fix(gaps):
                await self.auto_fix_gaps(gaps)
```

### Automatic Gap Remediation System

```python
# triangulation/auto_remediation.py

class AutomaticGapRemediation:
    """
    Automatically fixes detected gaps without human intervention
    """
    
    def __init__(self):
        self.remediation_strategies = {
            'prompt_to_thought': self.remediate_missing_thought,
            'thought_to_doc': self.remediate_missing_documentation,
            'prompt_to_doc': self.remediate_missing_requirement,
            'clarity_issue': self.remediate_clarity,
            'concept_drift': self.remediate_drift
        }
        self.sequential_thinking = SequentialThinkingMCP()
        
    async def remediate_gap(self, gap: Dict) -> bool:
        """
        Automatically fix a detected gap
        Returns True if successful
        """
        gap_type = gap['type']
        
        if gap_type in self.remediation_strategies:
            strategy = self.remediation_strategies[gap_type]
            return await strategy(gap)
        
        return False
    
    async def remediate_missing_thought(self, gap: Dict) -> bool:
        """Fix: User requirement not in thinking"""
        requirement = gap['requirement']
        
        # Use Sequential Thinking to reason about requirement
        thought_session = await self.sequential_thinking.think_through(
            problem=f"Analyze requirement: {requirement}",
            context=gap['source'],
            min_thoughts=5
        )
        
        # Append new thoughts to log
        await self.append_thoughts(thought_session.thoughts)
        
        # Verify fix
        return await self.verify_remediation(gap)
    
    async def remediate_missing_documentation(self, gap: Dict) -> bool:
        """Fix: Thought/decision not in documentation"""
        decision = gap['decision']
        thought = gap['thought']
        
        # Generate documentation update
        doc_update = await self.generate_documentation(decision, thought)
        
        # Apply update to appropriate file
        target_file = self.identify_target_file(decision)
        await self.update_file(target_file, doc_update)
        
        # Verify fix
        return await self.verify_remediation(gap)
    
    async def remediate_missing_requirement(self, gap: Dict) -> bool:
        """Fix: Critical requirement not implemented"""
        requirement = gap['requirement']
        
        # This is critical - use full Sequential Thinking
        solution = await self.sequential_thinking.think_through(
            problem=f"Implement missing requirement: {requirement}",
            context=self.get_full_context(),
            min_thoughts=10,
            max_thoughts=25
        )
        
        # Generate implementation
        implementation = await self.generate_implementation(solution)
        
        # Apply implementation
        await self.apply_implementation(implementation)
        
        # Run tests
        tests_pass = await self.run_tests(implementation)
        
        return tests_pass
```

### Continuous Learning System

```python
# triangulation/continuous_learning.py

class ContinuousLearningSystem:
    """
    Learns from gap patterns to prevent future occurrences
    """
    
    def __init__(self):
        self.gap_history = []
        self.pattern_database = {}
        self.prevention_strategies = {}
        
    def learn_from_gap(self, gap: Dict, remediation_success: bool):
        """Learn from each gap occurrence"""
        # Record gap
        self.gap_history.append({
            'gap': gap,
            'timestamp': datetime.now(),
            'remediation_success': remediation_success
        })
        
        # Identify pattern
        pattern = self.identify_pattern(gap)
        
        if pattern not in self.pattern_database:
            self.pattern_database[pattern] = {
                'occurrences': 0,
                'successful_remediations': 0,
                'contexts': []
            }
        
        # Update pattern statistics
        self.pattern_database[pattern]['occurrences'] += 1
        if remediation_success:
            self.pattern_database[pattern]['successful_remediations'] += 1
        self.pattern_database[pattern]['contexts'].append(gap)
        
        # Generate prevention strategy if pattern is recurring
        if self.pattern_database[pattern]['occurrences'] > 3:
            self.generate_prevention_strategy(pattern)
    
    def generate_prevention_strategy(self, pattern: str):
        """Create strategy to prevent this gap pattern"""
        contexts = self.pattern_database[pattern]['contexts']
        
        # Analyze common factors
        common_factors = self.analyze_common_factors(contexts)
        
        # Generate prevention rule
        prevention_rule = {
            'pattern': pattern,
            'triggers': common_factors,
            'prevention_action': self.determine_prevention_action(pattern, common_factors),
            'auto_apply': True
        }
        
        self.prevention_strategies[pattern] = prevention_rule
        
        # Apply prevention immediately
        self.apply_prevention_strategy(prevention_rule)
```

### Session Export and Analysis Tools

```python
# triangulation/session_export.py

class SessionExportAnalyzer:
    """
    Implements the user's recipe for session export and analysis
    But makes it automatic and programmatic
    """
    
    def __init__(self):
        self.session_log = []
        self.user_prompts = []
        self.sequential_thoughts = []
        
    async def auto_export_session(self) -> Dict:
        """Automatically export and analyze current session"""
        # Get current session from Claude Code
        session_data = await self.get_current_session()
        
        # Extract user prompts automatically
        self.user_prompts = self.extract_user_prompts(session_data)
        
        # Extract sequential thoughts
        self.sequential_thoughts = self.extract_sequential_thoughts(session_data)
        
        # Perform triangulation
        analysis = await self.triangulate_session()
        
        # Generate report
        report = self.generate_session_report(analysis)
        
        return {
            'user_prompts': self.user_prompts,
            'sequential_thoughts': self.sequential_thoughts,
            'analysis': analysis,
            'report': report
        }
    
    def extract_user_prompts(self, session_data: str) -> List[str]:
        """Extract all user messages from session"""
        prompts = []
        
        # Find all user messages
        pattern = r'<user_message>(.*?)</user_message>'
        matches = re.findall(pattern, session_data, re.DOTALL)
        
        for match in matches:
            # Clean and store
            clean_prompt = self.clean_prompt(match)
            prompts.append({
                'content': clean_prompt,
                'timestamp': self.extract_timestamp(match),
                'context': self.extract_context(match)
            })
        
        return prompts
    
    def extract_sequential_thoughts(self, session_data: str) -> List[str]:
        """Extract all sequential thinking outputs"""
        thoughts = []
        
        # Multiple patterns to catch different formats
        patterns = [
            r'Thought \d+:(.*?)(?=Thought \d+:|$)',
            r'### Thought \d+(.*?)(?=### Thought|$)',
            r'"thought":\s*"(.*?)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, session_data, re.DOTALL)
            thoughts.extend(matches)
        
        # Deduplicate and order
        thoughts = self.deduplicate_thoughts(thoughts)
        
        return thoughts
    
    async def triangulate_session(self) -> Dict:
        """Perform comprehensive session triangulation"""
        gaps = []
        insights = []
        
        # Check each user prompt
        for prompt in self.user_prompts:
            # Was it addressed in thinking?
            addressed_in_thought = self.check_prompt_in_thoughts(
                prompt, self.sequential_thoughts
            )
            
            if not addressed_in_thought:
                gaps.append({
                    'type': 'unaddressed_prompt',
                    'prompt': prompt,
                    'severity': 'high'
                })
            
            # Was it implemented?
            implemented = await self.check_prompt_implementation(prompt)
            
            if not implemented:
                gaps.append({
                    'type': 'unimplemented_prompt',
                    'prompt': prompt,
                    'severity': 'critical'
                })
        
        # Check each thought
        for thought in self.sequential_thoughts:
            # Was it requested by user?
            user_requested = self.check_thought_requested(
                thought, self.user_prompts
            )
            
            # Was it documented?
            documented = await self.check_thought_documented(thought)
            
            if user_requested and not documented:
                gaps.append({
                    'type': 'undocumented_thought',
                    'thought': thought,
                    'severity': 'medium'
                })
        
        # Generate insights
        insights = self.generate_insights(gaps)
        
        return {
            'gaps': gaps,
            'insights': insights,
            'alignment_score': self.calculate_alignment(gaps)
        }
```

### Integration with Claude Code Workflow

```python
# triangulation/claude_code_integration.py

class ClaudeCodeTriangulationIntegration:
    """
    Deep integration with Claude Code workflow
    """
    
    def __init__(self):
        self.ats = AutomatedTriangulationSystem()
        self.qa_multipliers = QualityAssuranceMultipliers()
        self.gap_detector = RealtimeGapDetector()
        self.remediator = AutomaticGapRemediation()
        self.learning_system = ContinuousLearningSystem()
        
        # Start all systems
        self.initialize_all_systems()
    
    def initialize_all_systems(self):
        """Start all triangulation systems"""
        # Start real-time monitoring
        self.gap_detector.start_monitoring()
        
        # Start continuous triangulation
        asyncio.create_task(self.ats.run_continuous_monitoring())
        
        # Enable auto-remediation
        self.remediator.enable_auto_fix = True
        
        # Start learning system
        self.learning_system.enable_learning = True
    
    async def on_claude_code_decision(self, decision: str, context: Dict):
        """Hook into every Claude Code decision"""
        # Use Sequential Thinking
        thought_session = await self.sequential_thinking.think_through(
            problem=decision,
            context=context
        )
        
        # Save thoughts immediately
        await self.save_thoughts(thought_session.thoughts)
        
        # Quick triangulation check
        alignment = await self.quick_alignment_check(
            thought_session.thoughts,
            decision
        )
        
        if alignment < 0.9:  # Less than 90% alignment
            # Alert and get confirmation
            await self.alert_alignment_issue(alignment, decision)
        
        return thought_session.solution
    
    async def on_file_write(self, file_path: str, content: str):
        """Hook into every file write operation"""
        # Check if content aligns with requirements
        gaps = await self.check_content_alignment(content)
        
        if gaps:
            # Attempt auto-correction
            corrected_content = await self.auto_correct_content(content, gaps)
            
            if corrected_content != content:
                # Alert user of corrections
                await self.alert_corrections(gaps, corrected_content)
                
                return corrected_content
        
        return content
```

---

## 🎯 System Overview

### Architecture Summary
```yaml
system:
  agents: 13 (5 Nuance + 8 Intelligence)
  orchestration: Dual-layer with semantic sync
  storage: ChromaDB (vectors) + Redis (cache)
  deployment: Docker containers with permission tiers
  security: Three-tier progressive model
  philosophy: "Revelation, not persuasion"
```

### Implementation Priority
1. **TODAY**: Core infrastructure + first agents
2. **Day 2**: Full agent deployment + workflows
3. **Day 3**: Testing + editorial materials
4. **Week 1**: Complete system + refinement

---

## 📁 Project Structure

```bash
Licia-Research-Lab-V2/
├── agents/
│   ├── nuance/                    # Context Guardian agents
│   │   ├── emotional_nuance.py
│   │   ├── somatic_detail.py
│   │   ├── research_connections.py
│   │   ├── therapeutic_applications.py
│   │   └── cultural_context.py
│   ├── intelligence/               # Intelligence layer agents
│   │   ├── emotional_intelligence.py
│   │   ├── somatic_intelligence.py
│   │   ├── theoretical_framework.py
│   │   ├── clinical_application.py
│   │   ├── workshop_intelligence.py
│   │   ├── publication_generation.py
│   │   ├── network_discovery.py
│   │   └── touch_flow_taxonomy.py
│   └── orchestrator.py            # Main coordination
├── workflows/
│   ├── editorial_sprint.py
│   ├── perplexity_ranking.py
│   ├── licia_enrichment.py
│   └── semantic_sync.py
├── memory/
│   ├── chromadb_manager.py
│   ├── redis_cache.py
│   └── rag_pipeline.py
├── security/
│   ├── sanitizer.py
│   ├── rate_limiter.py
│   └── audit_logger.py
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.agents
│   └── Dockerfile.orchestrator
├── config/
│   ├── claude.yaml                # Claude Code settings
│   ├── .clinerules                # Auto-approve patterns
│   ├── agent_configs/
│   └── mcp_configs/
├── outputs/
│   ├── editorial/
│   ├── chapters/
│   └── visualizations/
└── tests/
    ├── agent_tests/
    └── integration_tests/
```

---

## 🤖 Agent Implementation Specifications

### Base Agent Class

```python
# agents/base_agent.py

from abc import ABC, abstractmethod
import asyncio
from typing import List, Dict, Any
import chromadb
import redis
from datetime import datetime

class BaseAgent(ABC):
    """
    Base class for all agents in the system
    """
    
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type  # 'nuance' or 'intelligence'
        self.tools = []
        self.semantic_vocabulary = {}
        self.chroma_client = chromadb.Client()
        self.redis_client = redis.Redis()
        self.tdai_threshold = 8.0  # Minimum quality score
        
    @abstractmethod
    async def analyze(self, content: str) -> Dict[str, Any]:
        """Main analysis method - must be implemented by each agent"""
        pass
    
    async def parallel_tool_execution(self, tools: List[callable]) -> List[Any]:
        """Execute multiple tools in parallel"""
        tasks = [asyncio.create_task(tool()) for tool in tools]
        results = await asyncio.gather(*tasks)
        return results
    
    def semantic_sync(self, shared_vocabulary: Dict) -> None:
        """Synchronize vocabulary with other agents"""
        self.semantic_vocabulary.update(shared_vocabulary)
        
    def calculate_tdai_score(self, analysis: Dict) -> float:
        """Calculate Therapeutic Depth Assessment Index"""
        # Implementation of TDAI scoring
        pass
    
    def save_to_memory(self, content: Any, metadata: Dict) -> None:
        """Save analysis to vector database"""
        embedding = self.generate_embedding(content)
        self.chroma_client.add(
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[f"{self.name}_{datetime.now().isoformat()}"]
        )
```

### Emotional Nuance Agent (Priority 1)

```python
# agents/nuance/emotional_nuance.py

class EmotionalNuanceAgent(BaseAgent):
    """
    Preserves feeling textures and affective subtleties
    """
    
    def __init__(self):
        super().__init__("emotional_nuance", "nuance")
        self.tools = [
            self.detect_micro_expressions,
            self.track_emotional_vocabulary,
            self.map_feeling_gradients,
            self.preserve_affective_context,
            self.identify_unconscious_patterns
        ]
        self.emotion_lexicon = self.load_emotion_lexicon()
        
    async def analyze(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze transcript for emotional nuance
        CRITICAL: Preserve ALL subtlety - never flatten
        """
        # Run tools in parallel
        results = await self.parallel_tool_execution(self.tools)
        
        analysis = {
            "micro_expressions": results[0],
            "emotional_vocabulary": results[1],
            "feeling_gradients": results[2],
            "affective_context": results[3],
            "unconscious_patterns": results[4],
            "nuance_preserved": True,
            "tdai_score": self.calculate_tdai_score(results)
        }
        
        # Save to memory
        self.save_to_memory(analysis, {
            "type": "emotional_nuance",
            "transcript_id": transcript.id,
            "timestamp": datetime.now()
        })
        
        return analysis
    
    async def detect_micro_expressions(self) -> List[Dict]:
        """Detect subtle emotional shifts"""
        # Implementation
        pass
    
    async def track_emotional_vocabulary(self) -> Dict:
        """Track emotion words and their evolution"""
        # Implementation
        pass
    
    # Additional tool implementations...
```

### Emotional Intelligence Agent (Priority 1)

```python
# agents/intelligence/emotional_intelligence.py

class EmotionalIntelligenceAgent(BaseAgent):
    """
    Adds pattern recognition and breakthrough detection
    Works WITH EmotionalNuanceAgent, not replacing it
    """
    
    def __init__(self):
        super().__init__("emotional_intelligence", "intelligence")
        self.tools = [
            self.pattern_recognition,
            self.emotional_contagion_mapping,
            self.breakthrough_detection,
            self.group_coherence_analysis,
            self.therapeutic_alliance_scoring,
            self.affect_correlation_matrix,
            self.emotion_evolution_tracking,
            self.emotional_trajectory_plotting
        ]
        
    async def analyze(self, transcript: str, nuance_analysis: Dict) -> Dict:
        """
        Add intelligence layer to nuance analysis
        CRITICAL: Never override nuance, only enhance
        """
        # Get nuance analysis first
        if not nuance_analysis:
            raise ValueError("Must have nuance analysis first!")
            
        # Run intelligence tools in parallel (8 tools)
        results = await self.parallel_tool_execution(self.tools)
        
        analysis = {
            "patterns_across_sessions": results[0],
            "emotional_contagion_map": results[1],
            "breakthrough_moments": results[2],
            "group_coherence_score": results[3],
            "therapeutic_alliance": results[4],
            "correlation_matrix": results[5],
            "evolution_timeline": results[6],
            "trajectory_plot": results[7],
            "nuance_preserved": nuance_analysis["nuance_preserved"],
            "intelligence_added": True
        }
        
        return analysis
```

---

## 🔄 Semantic Synchronization Implementation

```python
# workflows/semantic_sync.py

import asyncio
from typing import List, Dict
import time

class SemanticSynchronizer:
    """
    Prevents compartmentalization while maintaining parallelization
    """
    
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
        self.shared_vocabulary = {
            "emotional": {},
            "somatic": {},
            "therapeutic": {},
            "cultural": {}
        }
        self.sync_interval = 30  # seconds
        self.audit_log = []
        
    async def run_sync_cycle(self):
        """
        Main synchronization cycle
        Pattern: 30s parallel work → 5s sync → 5s integration
        """
        while True:
            # Phase 1: Parallel work (30 seconds)
            await asyncio.sleep(30)
            
            # Phase 2: Vocabulary sync (5 seconds)
            start_sync = time.time()
            await self.synchronize_vocabulary()
            
            # Phase 3: Integration check (5 seconds)
            await self.check_integration()
            
            # Log the cycle
            self.audit_log.append({
                "timestamp": time.time(),
                "vocabulary_size": len(self.shared_vocabulary),
                "divergences": self.detect_divergences()
            })
            
    async def synchronize_vocabulary(self):
        """Sync vocabulary across all agents"""
        for agent in self.agents:
            # Collect vocabulary from each agent
            agent_vocab = agent.semantic_vocabulary
            
            # Merge into shared vocabulary
            for domain, terms in agent_vocab.items():
                self.shared_vocabulary[domain].update(terms)
        
        # Push updated vocabulary back to all agents
        for agent in self.agents:
            agent.semantic_sync(self.shared_vocabulary)
    
    def detect_divergences(self) -> List[Dict]:
        """Detect when agents use different terms for same concept"""
        divergences = []
        # Implementation to detect vocabulary conflicts
        return divergences
```

---

## 🐳 Docker Configuration

```yaml
# docker/docker-compose.yml
version: '3.9'

networks:
  licia-network:
    driver: bridge

services:
  # Vector Database
  chromadb:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: licia-chromadb
    ports:
      - "8000:8000"
    volumes:
      - ./chroma-data:/chroma/chroma/
    environment:
      - IS_PERSISTENT=TRUE
    networks:
      - licia-network
      
  # Cache Layer
  redis:
    image: redis:alpine
    container_name: licia-redis
    ports:
      - "6379:6379"
    volumes:
      - ./redis-data:/data
    networks:
      - licia-network
      
  # High Permission Agents
  agents-high:
    build:
      context: .
      dockerfile: docker/Dockerfile.agents
    container_name: licia-agents-high
    environment:
      - PERMISSION_LEVEL=high
      - AUTO_APPROVE=true
    volumes:
      - ./workspace:/workspace:rw
      - ./memory:/memory:rw
    networks:
      - licia-network
      
  # Medium Permission Agents
  agents-medium:
    build:
      context: .
      dockerfile: docker/Dockerfile.agents
    container_name: licia-agents-medium
    environment:
      - PERMISSION_LEVEL=medium
      - AUTO_APPROVE=partial
    volumes:
      - ./workspace:/workspace:ro
    networks:
      - licia-network
```

---

## 🔐 Security Implementation (Tier 1 - Today)

```python
# security/sanitizer.py

import unicodedata
import re
import hashlib
from datetime import datetime
from typing import Optional

class SecurityTier1:
    """
    Basic but effective security - 70% protection in 2 hours
    """
    
    def __init__(self):
        # Zero-width characters that can hide attacks
        self.zero_width = re.compile(r'[\u200b\u200c\u200d\u2060\ufeff]')
        
        # Known injection patterns
        self.injection_patterns = [
            'ignore previous',
            'disregard above',
            'system prompt:',
            'sudo',
            '```python'
        ]
    
    def sanitize_input(self, text: str) -> str:
        """Fast, effective sanitization"""
        # 1. Normalize Unicode to canonical form
        text = unicodedata.normalize('NFC', text)
        
        # 2. Strip zero-width characters
        text = self.zero_width.sub('', text)
        
        # 3. Check for injection attempts
        normalized_lower = text.lower()
        for pattern in self.injection_patterns:
            if pattern in normalized_lower:
                # Log and neutralize
                self.log_injection_attempt(text, pattern)
                text = f"<POTENTIAL_INJECTION_BLOCKED>{text}</BLOCKED>"
        
        # 4. Length limit to prevent bombs
        return text[:100000]  # 100KB max
    
    def safe_filename(self, original: str) -> str:
        """Deterministic safe naming"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_8 = hashlib.sha256(original.encode()).hexdigest()[:8]
        safe_desc = re.sub(r'[^a-zA-Z0-9_-]', '', original)[:20]
        
        return f"{timestamp}_{hash_8}_{safe_desc}"
    
    def log_injection_attempt(self, text: str, pattern: str):
        """Log potential attacks for analysis"""
        with open('security/injection_log.txt', 'a') as f:
            f.write(f"{datetime.now()}: Pattern '{pattern}' detected\n")
```

---

## 🎮 Claude Code Configuration

### Auto-Approve Settings

```yaml
# config/claude.yaml

agents:
  emotional_nuance:
    auto_approve:
      - read_file
      - write_file
      - list_files
    manual_approve:
      - execute_command
      - api_calls
    
  emotional_intelligence:
    auto_approve:
      - read_file
      - write_file
      - list_files
      - chromadb_operations
    manual_approve:
      - execute_command
      
checkpoints:
  - after: "pattern_synthesis"
    notify: true
    pause: false
  - after: "chapter_generation"
    notify: true
    pause: true
  - on_error: always
    notify: true
    pause: true
    
notifications:
  desktop: true
  sound: true
  webhook: "http://localhost:3000/notifications"
```

### .clinerules Configuration

```markdown
# config/.clinerules

## Auto-Approve Patterns
- Allow all file operations in `transcripts/` directory
- Allow all file operations in `outputs/` directory
- Allow reading from `memory/` directory
- Allow ChromaDB operations
- Allow Redis cache operations

## Manual Approve Required
- Any `execute_command` operations
- External API calls
- File operations outside project directory
- Database schema changes
- Docker container management

## Checkpoint Notifications
When reaching these points, notify user:
- After processing each transcript
- Before generating chapter drafts
- When TDAI score < 8
- On any security warnings
```

---

## 🧪 Test & Refinement Workflow

```python
# tests/refinement_workflow.py

import json
from typing import Dict, List
from pathlib import Path

class RefinementWorkflow:
    """
    Iterative refinement with user feedback
    """
    
    def __init__(self):
        self.test_transcripts = [
            "samples/transcript_1.txt",
            "samples/transcript_2.txt",
            "samples/transcript_3.txt"
        ]
        self.feedback_forms = []
        
    async def run_baseline_test(self) -> Dict:
        """Phase 1: Baseline testing"""
        results = {}
        
        for transcript in self.test_transcripts:
            # Run all agents
            analysis = await self.process_transcript(transcript)
            results[transcript] = analysis
            
        return results
    
    def collect_user_feedback(self, results: Dict) -> Dict:
        """Phase 2: Structured feedback collection"""
        feedback_template = {
            "emotional_accuracy": 0,  # 1-10
            "somatic_completeness": 0,  # 1-10
            "research_integration": 0,  # 1-10
            "natural_revelation": 0,  # 1-10
            "comments": "",
            "specific_improvements": []
        }
        
        # Present results to user
        print("Please review the following outputs:")
        for transcript, analysis in results.items():
            print(f"\n{transcript}:")
            print(json.dumps(analysis, indent=2))
            
        # Collect feedback
        feedback = input("Enter feedback (JSON format): ")
        return json.loads(feedback)
    
    def adjust_parameters(self, feedback: Dict):
        """Phase 3: Parameter adjustment based on feedback"""
        adjustments = {}
        
        if feedback["emotional_accuracy"] < 8:
            adjustments["emotion_sensitivity"] = 1.2
            
        if feedback["natural_revelation"] < 8:
            adjustments["research_embedding_subtlety"] = 1.5
            
        # Apply adjustments to agents
        self.apply_adjustments(adjustments)
        
    async def validate_improvements(self) -> bool:
        """Phase 4: Re-run and validate"""
        # Re-run same transcripts
        new_results = await self.run_baseline_test()
        
        # Compare with baseline
        improvement = self.calculate_improvement(new_results)
        
        return improvement > 0.1  # 10% improvement threshold
```

---

## 🚀 Quick Start Commands

### Initial Setup
```bash
# 1. Clone repository
git clone https://github.com/treaties-ai/Licia-s-Research-Lab-v2.git
cd Licia-Research-Lab-V2

# 2. Install dependencies
pip install -r requirements.txt
npm install  # for MCP servers

# 3. Start infrastructure
docker-compose up -d chromadb redis

# 4. Initialize database
python scripts/init_chromadb.py

# 5. Configure Claude Code
cp config/claude.yaml.template config/claude.yaml
cp config/.clinerules.template config/.clinerules
```

### Running First Agent
```python
# scripts/run_first_agent.py

import asyncio
from agents.nuance.emotional_nuance import EmotionalNuanceAgent
from agents.intelligence.emotional_intelligence import EmotionalIntelligenceAgent

async def main():
    # Initialize agents
    nuance_agent = EmotionalNuanceAgent()
    intelligence_agent = EmotionalIntelligenceAgent()
    
    # Load sample transcript
    with open("samples/transcript_1.txt", "r") as f:
        transcript = f.read()
    
    # Run nuance analysis first
    print("Running emotional nuance analysis...")
    nuance_analysis = await nuance_agent.analyze(transcript)
    
    # Add intelligence layer
    print("Adding intelligence layer...")
    full_analysis = await intelligence_agent.analyze(transcript, nuance_analysis)
    
    # Save output
    with open("outputs/first_analysis.json", "w") as f:
        json.dump(full_analysis, f, indent=2)
    
    print("Analysis complete! Check outputs/first_analysis.json")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 MCP Server Integration

### Sequential Thinking MCP Setup
```bash
# Install Sequential Thinking MCP
npm install -g @modelcontextprotocol/server-sequential-thinking

# Configure for agents
cat > config/mcp_configs/sequential_thinking.yaml << EOF
server: sequential-thinking
config:
  max_thoughts: 25
  preserve_history: true
  storage_path: memory/sequential_thinking/
EOF
```

### Integration Pattern
```python
# agents/mcp_integration.py

from mcp import SequentialThinkingClient

class MCPEnabledAgent(BaseAgent):
    """Base class for agents with MCP capabilities"""
    
    def __init__(self):
        super().__init__()
        self.sequential_thinking = SequentialThinkingClient()
        
    async def deep_analysis(self, problem: str) -> Dict:
        """Use Sequential Thinking for complex analysis"""
        thinking_session = await self.sequential_thinking.start_session(
            problem=problem,
            max_thoughts=15
        )
        
        # Let it think through the problem
        result = await thinking_session.think_through()
        
        return result
```

---

## 🔄 Agent Evolution System

```python
# agents/evolution_system.py

class AgentEvolutionSystem:
    """
    Manages methodological evolution with candidate queue
    """
    
    def __init__(self):
        self.candidate_queue = []
        self.methodological_core = {
            "preserve_nuance": True,
            "honor_embodied_wisdom": True,
            "maintain_scientific_rigor": True,
            "center_marginalized_voices": True
        }
        
    def observe_pattern(self, pattern: Dict):
        """Observe recurring patterns in Licia's work"""
        if self.is_significant(pattern):
            candidate = self.generate_candidate(pattern)
            self.candidate_queue.append(candidate)
    
    def test_candidate(self, candidate: Dict) -> bool:
        """Test in sandbox environment"""
        # Create isolated test environment
        sandbox = self.create_sandbox()
        
        # Test candidate
        baseline_score = sandbox.run_baseline()
        candidate_score = sandbox.run_with_candidate(candidate)
        
        return candidate_score > baseline_score * 1.1
    
    def gradual_rollout(self, candidate: Dict):
        """Progressive deployment"""
        # Stage 1: 10% of processing
        self.deploy_to_percentage(candidate, 0.1)
        
        # Monitor for issues
        if self.monitor_success():
            # Stage 2: 50%
            self.deploy_to_percentage(candidate, 0.5)
            
            if self.monitor_success():
                # Stage 3: Full deployment
                self.deploy_to_percentage(candidate, 1.0)
```

---

## ✅ Implementation Checklist

### Day 1 (TODAY)
- [ ] Set up Docker infrastructure
- [ ] Initialize ChromaDB and Redis
- [ ] Create security Tier 1 module
- [ ] Implement Emotional Nuance Agent
- [ ] Implement Emotional Intelligence Agent
- [ ] Test semantic synchronization
- [ ] Generate first editorial materials

### Day 2
- [ ] Complete all 5 Context Guardians
- [ ] Deploy 3 more Intelligence Agents
- [ ] Implement Perplexity ranking workflow
- [ ] Set up Licia enrichment pipeline
- [ ] Run integration tests

### Day 3
- [ ] Complete all 13 agents
- [ ] Full workflow testing
- [ ] Generate chapter drafts
- [ ] Create editorial package
- [ ] Team training

### Week 1
- [ ] Sequential Thinking MCP integration
- [ ] Evolution system activation
- [ ] Security Tier 2 implementation
- [ ] Performance optimization
- [ ] Scale for production

---

## 🆘 Troubleshooting

### Common Issues

#### ChromaDB Connection Failed
```bash
# Check if ChromaDB is running
docker ps | grep chromadb

# Restart if needed
docker-compose restart chromadb

# Check logs
docker logs licia-chromadb
```

#### Agent Memory Overflow
```python
# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
```

#### Semantic Sync Lag
```python
# Reduce sync interval if needed
synchronizer.sync_interval = 15  # From 30 seconds
```

---

## 📞 Support & Next Steps

### Critical Contacts
- **Technical Issues**: Check logs in `logs/` directory
- **Agent Behavior**: Review TDAI scores in outputs
- **Security Alerts**: Check `security/audit_log.txt`

### Next Context Window
If context window fills, start new session with:
1. Read `NEXT_CONTEXT_IMPLEMENTATION_PLAN.md`
2. Check implementation status
3. Continue with uncompleted items
4. Focus on editorial sprint needs

---

*This implementation guide provides everything needed to build Licia's Research Lab V2. Follow the priority order, maintain the philosophy of "revelation not persuasion," and remember that this system serves a sacred purpose: preserving and amplifying healing wisdom that will touch millions of lives.*
