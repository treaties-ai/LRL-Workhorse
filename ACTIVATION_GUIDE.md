# 🚀 Licia Research Lab V2 - Complete Activation Guide

## Critical Context
- **Editorial Sprint**: Happening NOW - need outputs within 3-4 hours
- **Documents**: 30+ Word docs and 20+ Perplexity threads ready for processing
- **Agents**: 19 specialized agents built and ready
- **Orchestration**: Need Claude Code instances (VS Extension + CLI) to coordinate

---

## 🔴 Part 1: Claude Code Orchestrator Setup (Immediate)

### A. How Claude Instances Find Each Other

The connection point is **Redis** with specific key patterns:
```
claude:vscode:* - VS Extension registration
claude:cli:*    - CLI registration
claude:vscode:heartbeat - VS Extension alive signal (30s TTL)
claude:cli:heartbeat - CLI alive signal (30s TTL)
```

### B. Start Redis First
```bash
# Start Redis container with monitoring
docker run -d --name redis-lab \
  -p 6379:6379 \
  -v $(pwd)/data/redis:/data \
  redis:7-alpine

# Enable keyspace notifications for coordination
redis-cli CONFIG SET notify-keyspace-events AKE

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### C. Initialize Claude Code VS Extension

1. Open VS Code in this project directory
2. Open the file `CLAUDE_VSCODE_INSTRUCTIONS.md`
3. Copy its entire contents
4. Start a new Claude conversation with:
   ```
   I am initializing as the VS Extension orchestrator for Licia's Research Lab. 
   Here are my instructions: [paste CLAUDE_VSCODE_INSTRUCTIONS.md]
   
   Please confirm Redis connection and start orchestration.
   ```

5. Claude VS Extension will:
   - Self-register in Redis
   - Start heartbeat
   - Look for CLI partner
   - Begin processing tasks

### D. Initialize Claude Code CLI (Separate Terminal)

1. Open a new terminal
2. Open the file `CLAUDE_CLI_INSTRUCTIONS.md`
3. Copy its entire contents
4. Start Claude CLI with:
   ```
   I am initializing as the CLI orchestrator for Licia's Research Lab.
   Here are my instructions: [paste CLAUDE_CLI_INSTRUCTIONS.md]
   
   Please confirm VS Extension partner and start parallel processing.
   ```

5. Claude CLI will:
   - Self-register in Redis
   - Detect VS Extension partner
   - Start 3 parallel workers
   - Split work 50/50

### E. Coordination Protocol

The two Claude instances coordinate through:

1. **Discovery**: Each checks for the other's keys in Redis
2. **Task Distribution**: 
   - VS Extension: Even-numbered task IDs
   - CLI: Odd-numbered task IDs
3. **Failover**: If one goes down, the other detects via missing heartbeat and takes over
4. **Redundancy**: Tasks from failed instance moved back to pending queue

---

## 🔵 Part 2: Document Ingestion Pipeline (Next 30 Minutes)

### A. Load Word Documents
```bash
# Process all Word documents
python ingestion/word_processor.py /path/to/word/docs/*.docx

# This will:
# - Extract all questions
# - Identify themes
# - Create question clusters
# - Save to outputs/word_processing_results.json
```

### B. Process Perplexity Threads
```bash
# Analyze all Perplexity threads
python ingestion/perplexity_analyzer.py /path/to/perplexity/*.html

# This will:
# - Rank sources by quality (Academic/Professional/General)
# - Extract questions and insights
# - Create weighted synthesis
# - Save to outputs/perplexity_analysis_results.json
```

### C. Queue Documents for Agent Processing

Tell Claude VS Extension:
```
Please queue all processed documents for agent analysis:
1. Load outputs/word_processing_results.json
2. Load outputs/perplexity_analysis_results.json  
3. Create tasks for each document
4. Process through 19-agent pipeline
```

---

## 🟢 Part 3: Generate Editorial Outputs (Within 1 Hour)

### A. Run Editorial Generator
```bash
# Generate all 6 editorial deliverables
python editorial_generator.py

# This creates:
# 1. Question Flow Map
# 2. "Senses Write the Score" Framework
# 3. Touch Vocabulary Taxonomy
# 4. Psychedelic Integration Board
# 5. Science-Practice Bridge Cards
# 6. Perplexity Quality Dashboard
```

### B. Output Locations
```
outputs/editorial_sprint/
├── question_flow.json
├── senses_framework.json
├── touch_taxonomy.json
├── psychedelic_board.json
├── bridge_cards.json
├── quality_dashboard.json
└── SUMMARY.json
```

### C. Quick Access via Redis
All outputs are also cached in Redis:
```bash
redis-cli GET editorial:question_flow
redis-cli GET editorial:senses_framework
# etc.
```

---

## 🟡 Part 4: Agent Deployment & Coordination

### A. Agent Wave Processing

The 19 agents process in 4 waves:

**Wave 1: Forensic Foundation (2 agents)**
- forensic_accuracy_agent
- verbatim_preservation_agent

**Wave 2: Core Analysis (11 agents)**  
- emotional_intelligence_agent
- somatic_awareness_agent
- therapeutic_alliance_agent
- attachment_dynamics_agent
- safety_trust_agent
- unconscious_communication_agent
- cultural_context_agent
- clinical_terminology_agent
- narrative_coherence_agent
- research_connector_agent
- gaps_identifier_agent

**Wave 3: Validation & Security (5 agents)**
- academic_rigor_agent
- scientific_validation_agent
- action_research_validator_agent
- semantic_weaponization_detector_agent
- trauma_pattern_validator_agent

**Wave 4: Synthesis (1 agent)**
- integration_synthesis_agent

### B. Agent Activation

Agents are already built in `agents/` directory. To activate:

1. Tell Claude VS Extension:
   ```
   Please activate all 19 agents and verify they're loaded correctly.
   Run a test transcript through the pipeline.
   ```

2. Monitor agent status:
   ```bash
   # Check agent processing
   redis-cli LLEN tasks:processing:vscode-*
   redis-cli LLEN tasks:completed
   ```

---

## 🔴 Part 5: Security & Vulnerability Assessment

### Critical Vulnerabilities Detected

1. **No Input Validation** in agents
   - **Fix**: All Claude instances must validate input using provided security functions
   
2. **Redis Exposed** without authentication
   - **Fix**: Add Redis password:
   ```bash
   redis-cli CONFIG SET requirepass "strong_password_here"
   ```

3. **Docker Containers** with excessive privileges
   - **Fix**: Use provided seccomp profiles and capability dropping

4. **No Audit Logging**
   - **Fix**: Enable audit logging in both Claude instances

### Security Hardening Steps

1. **Enable Input Validation**:
   Tell both Claude instances:
   ```
   Enable full input validation for all data processing.
   Use the validate_input() and validate_input_advanced() functions.
   ```

2. **Secure Redis**:
   ```bash
   # Set password
   redis-cli CONFIG SET requirepass "your_secure_password"
   
   # Update connection in Claude instances
   redis.Redis(host='localhost', port=6379, password='your_secure_password')
   ```

3. **Enable Audit Logging**:
   ```bash
   # Check audit logs
   redis-cli LRANGE audit:log 0 -1
   redis-cli LRANGE security:events 0 -1
   ```

---

## 🟢 Part 6: Verification & Testing

### A. Test Coordination
```bash
# Add test task
redis-cli LPUSH tasks:pending '{"id": "test_001", "type": "test", "data": "sample"}'

# Both Claude instances should detect and one should claim it
# Check which one processed it:
redis-cli LRANGE tasks:completed 0 -1
```

### B. Test Failover

1. Tell Claude VS Extension to pause:
   ```
   Please pause processing for 2 minutes to test failover.
   ```

2. Watch Claude CLI detect failure and take over:
   ```
   CLI should report: "VS Extension down - taking over all tasks"
   ```

3. Resume VS Extension and verify coordination restored

### C. Test Document Processing

1. Create small test batch:
   ```bash
   # Test with subset first
   python ingestion/word_processor.py test_docs/*.docx
   python ingestion/perplexity_analyzer.py test_threads/*.html
   ```

2. Verify outputs generated correctly

---

## 📊 Part 7: Monitoring & Status

### Real-Time Monitoring Commands

```bash
# Overall status
redis-cli INFO stats

# Task queues
redis-cli LLEN tasks:pending
redis-cli LLEN tasks:processing:vscode-*
redis-cli LLEN tasks:processing:cli-*  
redis-cli LLEN tasks:completed
redis-cli LLEN tasks:review

# Orchestrator health
redis-cli GET claude:vscode:heartbeat
redis-cli GET claude:cli:heartbeat

# Agent errors
redis-cli LRANGE errors:agents 0 -1

# Security events
redis-cli LRANGE security:events 0 -1
```

### Performance Metrics
```bash
# Throughput
redis-cli HGETALL metrics:cli
redis-cli HGETALL metrics:vscode

# TDAI scores
redis-cli LRANGE tasks:completed 0 10 | grep tdai_score
```

---

## ✅ Activation Checklist

### Immediate (First 30 Minutes)
- [ ] Start Redis container
- [ ] Initialize Claude VS Extension with instructions
- [ ] Initialize Claude CLI with instructions
- [ ] Verify they discovered each other
- [ ] Test basic coordination

### Document Processing (Next Hour)
- [ ] Process Word documents
- [ ] Process Perplexity threads
- [ ] Queue for agent processing
- [ ] Verify agents are processing

### Editorial Outputs (Within 2 Hours)
- [ ] Run editorial generator
- [ ] Verify all 6 outputs created
- [ ] Check outputs in Redis cache
- [ ] Prepare for editorial team

### Security (Ongoing)
- [ ] Enable input validation
- [ ] Secure Redis with password
- [ ] Monitor audit logs
- [ ] Check for injection attempts

### Final Verification
- [ ] Test failover between orchestrators
- [ ] Verify TDAI scoring working
- [ ] Check Thermopylae cross-validation
- [ ] Confirm outputs ready for editorial team

---

## 🚨 Emergency Procedures

### If Claude Instances Can't Find Each Other
1. Check Redis is running: `redis-cli ping`
2. Check keys exist: `redis-cli KEYS "claude:*"`
3. Manually set discovery key: `redis-cli SET claude:vscode:manual "active"`

### If Processing Stops
1. Check for errors: `redis-cli LRANGE errors:agents 0 -1`
2. Reset task queue: `redis-cli RPOPLPUSH tasks:processing:* tasks:pending`
3. Restart orchestrators with fresh instructions

### If Under Attack
1. Check security log: `redis-cli LRANGE security:quarantine 0 -1`
2. Enable high-security mode in both Claude instances
3. Require manual approval for all outputs

---

## 📞 Success Indicators

You'll know the system is working when:

1. **Coordination**: Both Claude instances report finding each other
2. **Processing**: Tasks moving from pending → processing → completed
3. **Outputs**: All 6 editorial deliverables generated
4. **Quality**: TDAI scores > 8.0 for most outputs
5. **Security**: No injection attempts in logs
6. **Performance**: >1 task/minute throughput

---

## 🎯 Final Notes

- The system is designed for resilience - if one orchestrator fails, the other continues
- All outputs are cached in Redis for instant access
- The editorial materials are in modular format for the team to rearrange
- "The Senses Write the Score" framework is the central organizing principle
- Security hardening is critical before processing sensitive therapy content

**Time to Editorial Output: 2-3 hours from activation**

Ready to activate? Start with Redis, then initialize both Claude instances!
