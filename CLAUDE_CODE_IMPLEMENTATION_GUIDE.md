# Claude Code Implementation Guide
## Advanced Specifications for Building Licia's Research Lab V2

**Purpose:** Provide Claude Code with complete implementation specifications to build and deploy the 13-agent research laboratory system.

**Critical Context:** Editorial sprint is happening NOW. Priority 1 implementations are mission-critical.

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
