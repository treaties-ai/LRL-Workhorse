# Rapid Implementation Guide: Licia's Research Lab V2
## Dual-Orchestrator Architecture for Maximum Throughput & Resilience

**Purpose:** Get multiple Claude Code agents running in parallel with proper security, testing, and human oversight to support the editorial team immediately.

**Architecture:** Dual orchestrator pathways (VSCode + CLI) for redundancy and forensic clarity.

---

## 🚀 Section 0: 30-Minute Quick Start

### Prerequisites Check
```bash
# Run this first to verify your environment
./scripts/check_prerequisites.sh

# Or manually verify:
docker --version  # Need 20.10+
python --version  # Need 3.9+
node --version    # Need 16+
redis-cli ping    # Should return PONG
```

### One-Command Setup
```bash
# Clone and initialize everything
git clone https://github.com/treaties-ai/Licia-Research-Lab-V2.git
cd Licia-Research-Lab-V2

# Run the rapid setup
make rapid-start

# This will:
# 1. Create directory structure
# 2. Pull Docker images
# 3. Initialize databases
# 4. Start core services
# 5. Run health checks
```

### Verify Installation
```bash
# Check all services are running
make status

# Expected output:
# ✅ ChromaDB: Running (port 8000)
# ✅ Redis: Running (port 6379)
# ✅ Task Queue: Ready
# ✅ Review Interface: http://localhost:3000
# ✅ Orchestrators: Ready to start
```

---

## 🎭 Section 1: Dual Orchestrator Setup

### Architecture Overview
```
┌─────────────────────────────────────────────────────┐
│                   User Interfaces                    │
├──────────────────────┬───────────────────────────────┤
│   VSCode Extension   │    Claude Code CLI           │
│   (Orchestrator 1)   │    (Orchestrator 2)          │
├──────────────────────┴───────────────────────────────┤
│              Redis Coordination Layer                │
│         (Task Queue + State Management)              │
├───────────────────────────────────────────────────────┤
│                 Docker Agent Farm                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │Agent 1  │  │Agent 2  │  │Agent 3  │  │Agent N  ││
│  │(Tier 1) │  │(Tier 2) │  │(Tier 2) │  │(Tier 3) ││
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘│
├───────────────────────────────────────────────────────┤
│         Shared Storage & Vector Database             │
│         (ChromaDB + File System + Redis)             │
└───────────────────────────────────────────────────────┘
```

### VSCode Orchestrator Setup

#### 1. Configure VSCode Extension
```yaml
# .vscode/licia-lab.yaml
orchestrator:
  mode: vscode
  id_prefix: "vscode"
  namespace: "vscode"
  
coordination:
  redis_host: localhost
  redis_port: 6379
  heartbeat_interval: 10  # seconds
  task_claim_timeout: 300  # 5 minutes
  
auto_approve:
  read_operations: true
  write_to_outputs: true
  docker_operations: false
  system_commands: false
  
checkpoints:
  - after: "transcript_processing"
  - after: "chapter_generation"
  - on_error: always
  
monitoring:
  log_path: "logs/vscode/"
  metrics_port: 9090
```

#### 2. Initialize VSCode Orchestrator
```python
# orchestrators/vscode_orchestrator.py

import redis
import uuid
from datetime import datetime
import asyncio

class VSCodeOrchestrator:
    """VSCode-based orchestrator for agent coordination"""
    
    def __init__(self):
        self.orchestrator_id = f"vscode-{uuid.uuid4().hex[:8]}"
        self.redis_client = redis.Redis(
            host='localhost', 
            port=6379,
            decode_responses=True
        )
        self.namespace = "vscode"
        self.running = False
        
    async def start(self):
        """Start the VSCode orchestrator"""
        self.running = True
        print(f"🚀 VSCode Orchestrator started: {self.orchestrator_id}")
        
        # Register with Redis
        self.redis_client.hset(
            "orchestrators:active",
            self.orchestrator_id,
            datetime.now().isoformat()
        )
        
        # Start heartbeat
        asyncio.create_task(self.heartbeat_loop())
        
        # Start task processing
        asyncio.create_task(self.process_tasks())
        
    async def heartbeat_loop(self):
        """Maintain heartbeat for health monitoring"""
        while self.running:
            self.redis_client.setex(
                f"orchestrator:{self.orchestrator_id}:alive",
                30,  # 30 second TTL
                datetime.now().isoformat()
            )
            await asyncio.sleep(10)
    
    async def process_tasks(self):
        """Main task processing loop"""
        while self.running:
            # Try to claim a task
            task = self.claim_next_task()
            if task:
                await self.execute_task(task)
            else:
                await asyncio.sleep(1)  # No tasks, wait
    
    def claim_next_task(self):
        """Atomically claim the next available task"""
        # Pop from pending queue
        task_id = self.redis_client.rpoplpush(
            "tasks:pending",
            f"tasks:processing:{self.orchestrator_id}"
        )
        
        if task_id:
            # Mark task as claimed
            claimed = self.redis_client.set(
                f"task:{task_id}:owner",
                self.orchestrator_id,
                nx=True,  # Only set if not exists
                ex=300    # 5 minute expiry
            )
            
            if claimed:
                # Load task details
                task_data = self.redis_client.hgetall(f"task:{task_id}")
                return {
                    'id': task_id,
                    'owner': self.orchestrator_id,
                    **task_data
                }
            else:
                # Another orchestrator claimed it
                return None
        return None
    
    async def execute_task(self, task):
        """Execute a claimed task"""
        print(f"📋 VSCode executing task: {task['id']}")
        
        try:
            # Dispatch to appropriate agent
            if task['type'] == 'transcript':
                await self.process_transcript(task)
            elif task['type'] == 'perplexity':
                await self.process_perplexity(task)
            elif task['type'] == 'synthesis':
                await self.process_synthesis(task)
            
            # Mark complete
            self.complete_task(task)
            
        except Exception as e:
            self.handle_task_error(task, e)
```

### CLI Orchestrator Setup

#### 1. Configure CLI Orchestrator
```yaml
# config/cli-orchestrator.yaml
orchestrator:
  mode: cli
  id_prefix: "cli"
  namespace: "cli"
  
coordination:
  redis_host: localhost
  redis_port: 6379
  heartbeat_interval: 10
  task_claim_timeout: 300
  
permissions:
  max_parallel_agents: 5
  memory_limit_per_agent: "2G"
  cpu_limit_per_agent: "1.0"
  
monitoring:
  log_path: "logs/cli/"
  metrics_port: 9091
```

#### 2. CLI Orchestrator Implementation
```python
# orchestrators/cli_orchestrator.py

import click
import redis
import uuid
from datetime import datetime
import asyncio

class CLIOrchestrator:
    """CLI-based orchestrator for agent coordination"""
    
    def __init__(self):
        self.orchestrator_id = f"cli-{uuid.uuid4().hex[:8]}"
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.namespace = "cli"
        self.running = False
        
    async def start(self):
        """Start the CLI orchestrator"""
        self.running = True
        click.echo(click.style(
            f"🚀 CLI Orchestrator started: {self.orchestrator_id}",
            fg='green'
        ))
        
        # Register with Redis
        self.redis_client.hset(
            "orchestrators:active",
            self.orchestrator_id,
            datetime.now().isoformat()
        )
        
        # Start concurrent tasks
        await asyncio.gather(
            self.heartbeat_loop(),
            self.process_tasks(),
            self.monitor_peer_orchestrator()
        )
    
    async def monitor_peer_orchestrator(self):
        """Monitor VSCode orchestrator status"""
        while self.running:
            vscode_keys = self.redis_client.keys("orchestrator:vscode-*:alive")
            
            if vscode_keys:
                click.echo(click.style("✅ VSCode orchestrator active", fg='green'))
            else:
                click.echo(click.style("⚠️ VSCode orchestrator not detected", fg='yellow'))
                # Could take over more tasks if needed
                
            await asyncio.sleep(30)

@click.command()
@click.option('--workers', default=3, help='Number of parallel workers')
@click.option('--mode', type=click.Choice(['solo', 'cooperative']), default='cooperative')
def start_cli_orchestrator(workers, mode):
    """Start the CLI orchestrator"""
    orchestrator = CLIOrchestrator()
    
    if mode == 'solo':
        click.echo("Running in SOLO mode - will process all tasks")
    else:
        click.echo("Running in COOPERATIVE mode - sharing with VSCode")
    
    asyncio.run(orchestrator.start())

if __name__ == '__main__':
    start_cli_orchestrator()
```

### Coordination Protocol

```python
# orchestrators/coordination.py

class OrchestratorCoordination:
    """Ensures VSCode and CLI orchestrators cooperate without conflicts"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def register_orchestrator(self, orchestrator_id, orchestrator_type):
        """Register an orchestrator as active"""
        registration = {
            'id': orchestrator_id,
            'type': orchestrator_type,
            'started': datetime.now().isoformat(),
            'tasks_completed': 0
        }
        
        self.redis.hset(
            'orchestrators:registry',
            orchestrator_id,
            json.dumps(registration)
        )
        
        # Log registration
        self.redis.lpush(
            f'logs:{orchestrator_type}',
            f"REGISTERED: {orchestrator_id}"
        )
    
    def task_arbitration(self, task_id):
        """Prevent duplicate processing through atomic operations"""
        # Use Redis WATCH for optimistic locking
        pipe = self.redis.pipeline()
        
        while True:
            try:
                pipe.watch(f'task:{task_id}:status')
                
                status = pipe.get(f'task:{task_id}:status')
                if status in ['processing', 'completed']:
                    return False  # Already being handled
                
                pipe.multi()
                pipe.set(f'task:{task_id}:status', 'processing')
                pipe.execute()
                return True  # Successfully claimed
                
            except redis.WatchError:
                continue  # Retry if another client modified
```

---

## 🔒 Section 2: Secure Virtual Environment

### Docker Security Architecture

#### Permission Tiers
```yaml
# docker/security-tiers.yaml

tiers:
  tier_1_readonly:
    capabilities:
      drop: [ALL]
      add: []
    volumes:
      - ./transcripts:/data/transcripts:ro
      - ./reference:/data/reference:ro
    network: none
    memory: 1G
    cpus: 0.5
    
  tier_2_processing:
    capabilities:
      drop: [ALL]
      add: [DAC_OVERRIDE]  # File access only
    volumes:
      - ./transcripts:/data/transcripts:ro
      - ./outputs:/data/outputs:rw
      - ./temp:/tmp:rw
    network: internal_only
    memory: 2G
    cpus: 1.0
    
  tier_3_orchestrator:
    capabilities:
      drop: [NET_ADMIN, SYS_ADMIN]
      add: [NET_BIND_SERVICE]
    volumes:
      - ./:/workspace:rw
    network: bridge
    memory: 4G
    cpus: 2.0
```

#### Docker Compose Configuration
```yaml
# docker-compose.secure.yml
version: '3.9'

networks:
  internal_only:
    internal: true
  bridge:
    driver: bridge

services:
  # Infrastructure
  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - ./data/redis:/data
    networks:
      - bridge
    restart: unless-stopped
    
  chromadb:
    image: ghcr.io/chroma-core/chroma:latest
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - ./data/chromadb:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
    networks:
      - bridge
    restart: unless-stopped
  
  # Tier 1: Read-only Analysis Agents
  agent_emotional_nuance:
    build:
      context: .
      dockerfile: docker/Dockerfile.agent
    environment:
      - AGENT_TYPE=emotional_nuance
      - PERMISSION_TIER=1
      - REDIS_HOST=redis
    volumes:
      - ./transcripts:/data/transcripts:ro
      - ./logs/agents:/logs:rw
    networks:
      - internal_only
    security_opt:
      - no-new-privileges:true
      - seccomp:seccomp/default.json
    read_only: true
    tmpfs:
      - /tmp
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    
  # Tier 2: Processing Agents
  agent_intelligence:
    build:
      context: .
      dockerfile: docker/Dockerfile.agent
    environment:
      - AGENT_TYPE=emotional_intelligence
      - PERMISSION_TIER=2
      - REDIS_HOST=redis
      - CHROMADB_HOST=chromadb
    volumes:
      - ./transcripts:/data/transcripts:ro
      - ./outputs:/data/outputs:rw
      - ./logs/agents:/logs:rw
    networks:
      - internal_only
    security_opt:
      - no-new-privileges:true
      - seccomp:seccomp/default.json
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    
  # Tier 3: Orchestrator Support
  task_queue:
    build:
      context: .
      dockerfile: docker/Dockerfile.celery
    environment:
      - CELERY_BROKER=redis://redis:6379/0
      - CELERY_BACKEND=redis://redis:6379/1
    volumes:
      - ./:/workspace:rw
    networks:
      - bridge
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

#### Security Profiles
```json
// seccomp/default.json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close",
        "stat", "fstat", "lstat",
        "mmap", "mprotect", "munmap",
        "brk", "rt_sigaction", "rt_sigprocmask",
        "access", "socket", "connect",
        "sendto", "recvfrom", "shutdown",
        "bind", "listen", "accept",
        "getsockname", "getpeername",
        "setsockopt", "getsockopt"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

### Agent Isolation & Communication

```python
# agents/secure_base_agent.py

import os
import redis
import json
from datetime import datetime
import hashlib

class SecureBaseAgent:
    """Base class with security controls for all agents"""
    
    def __init__(self, agent_type, permission_tier):
        self.agent_type = agent_type
        self.permission_tier = permission_tier
        self.agent_id = f"{agent_type}-{os.environ.get('HOSTNAME', 'local')}"
        
        # Restricted Redis connection
        self.redis = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'redis'),
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Audit all operations
        self.audit_log = []
        
    def validate_input(self, data):
        """Security validation for all inputs"""
        # Size limits
        if len(data) > 10_000_000:  # 10MB max
            raise ValueError("Input exceeds size limit")
        
        # Unicode sanitization
        import unicodedata
        data = unicodedata.normalize('NFC', data)
        
        # Remove zero-width characters
        zero_width = [
            '\u200b', '\u200c', '\u200d', 
            '\u2060', '\ufeff'
        ]
        for char in zero_width:
            data = data.replace(char, '')
        
        # Check for injection patterns
        injection_patterns = [
            'ignore previous',
            'disregard above',
            'system prompt',
            '```python'
        ]
        
        lower_data = data.lower()
        for pattern in injection_patterns:
            if pattern in lower_data:
                self.log_security_event(
                    'INJECTION_ATTEMPT',
                    {'pattern': pattern}
                )
                raise ValueError(f"Potential injection detected: {pattern}")
        
        return data
    
    def process_with_limits(self, data):
        """Process data with resource limits"""
        import resource
        
        # Set memory limit (1GB for Tier 1, 2GB for Tier 2)
        memory_limit = 1_073_741_824 if self.permission_tier == 1 else 2_147_483_648
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_limit, memory_limit)
        )
        
        # Set CPU time limit (30 seconds)
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (30, 30)
        )
        
        try:
            # Validate input
            clean_data = self.validate_input(data)
            
            # Process
            result = self.analyze(clean_data)
            
            # Sign output for integrity
            result['signature'] = self.sign_output(result)
            
            return result
            
        except Exception as e:
            self.log_security_event('PROCESSING_ERROR', {'error': str(e)})
            raise
    
    def sign_output(self, data):
        """Create integrity signature for output"""
        content = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(
            f"{self.agent_id}:{content}".encode()
        ).hexdigest()
        return signature
    
    def log_security_event(self, event_type, details):
        """Log security-relevant events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'event_type': event_type,
            'details': details
        }
        
        # Local audit log
        self.audit_log.append(event)
        
        # Central security log
        self.redis.lpush(
            'security:events',
            json.dumps(event)
        )
        
        # Alert on critical events
        if event_type in ['INJECTION_ATTEMPT', 'BREACH_DETECTED']:
            self.redis.publish(
                'security:alerts',
                json.dumps(event)
            )
```

---

## 🧪 Section 3: Core System Testing

### Test Suite Structure
```
tests/
├── unit/
│   ├── test_agents.py
│   ├── test_orchestrators.py
│   └── test_security.py
├── integration/
│   ├── test_agent_communication.py
│   ├── test_semantic_sync.py
│   └── test_task_distribution.py
├── e2e/
│   ├── test_transcript_processing.py
│   ├── test_perplexity_ingestion.py
│   └── test_full_pipeline.py
└── performance/
    ├── test_parallel_execution.py
    └── test_load_handling.py
```

### Critical Test: Agent Interplay

```python
# tests/integration/test_agent_communication.py

import pytest
import asyncio
import redis
from agents import EmotionalNuanceAgent, EmotionalIntelligenceAgent
from orchestrators import VSCodeOrchestrator, CLIOrchestrator

class TestAgentInterplay:
    """Test agent-to-agent communication and coordination"""
    
    @pytest.fixture
    def redis_client(self):
        """Provide clean Redis instance for testing"""
        client = redis.Redis(host='localhost', port=6379)
        client.flushdb()  # Clean slate
        yield client
        client.flushdb()  # Cleanup
    
    @pytest.mark.asyncio
    async def test_semantic_synchronization(self, redis_client):
        """Verify agents share vocabulary without conflicts"""
        # Initialize agents
        nuance_agent = EmotionalNuanceAgent()
        intelligence_agent = EmotionalIntelligenceAgent()
        
        # Process same content
        test_transcript = """
        Patient: I feel this tightness in my chest when I think about it.
        Therapist: Can you describe where exactly you feel it?
        Patient: Right here, like a fist squeezing my heart.
        """
        
        # Both agents analyze
        nuance_result = await nuance_agent.analyze(test_transcript)
        intel_result = await intelligence_agent.analyze(
            test_transcript, 
            nuance_result
        )
        
        # Check vocabulary alignment
        nuance_terms = nuance_result.get('emotional_vocabulary', {})
        intel_terms = intel_result.get('emotional_vocabulary', {})
        
        # Should have overlapping terms
        overlap = set(nuance_terms.keys()) & set(intel_terms.keys())
        assert len(overlap) > 0, "Agents should share vocabulary"
        
        # Should not have conflicting definitions
        for term in overlap:
            assert nuance_terms[term] == intel_terms[term], \
                f"Agents have conflicting definitions for '{term}'"
    
    @pytest.mark.asyncio
    async def test_dual_orchestrator_cooperation(self, redis_client):
        """Test VSCode and CLI orchestrators working together"""
        # Start both orchestrators
        vscode_orch = VSCodeOrchestrator()
        cli_orch = CLIOrchestrator()
        
        # Add test tasks
        for i in range(10):
            redis_client.lpush('tasks:pending', f'test_task_{i}')
            redis_client.hset(
                f'task:test_task_{i}',
                mapping={
                    'type': 'test',
                    'data': f'content_{i}'
                }
            )
        
        # Run both orchestrators briefly
        vscode_task = asyncio.create_task(vscode_orch.start())
        cli_task = asyncio.create_task(cli_orch.start())
        
        # Let them process
        await asyncio.sleep(5)
        
        # Stop orchestrators
        vscode_orch.running = False
        cli_orch.running = False
        
        await vscode_task
        await cli_task
        
        # Check results
        pending = redis_client.llen('tasks:pending')
        assert pending == 0, "All tasks should be processed"
        
        # Check for conflicts (no task processed twice)
        processed = []
        for key in redis_client.keys('task:test_task_*:owner'):
            owner = redis_client.get(key)
            task_id = key.split(':')[1]
            assert task_id not in processed, f"Task {task_id} processed multiple times"
            processed.append(task_id)
        
        assert len(processed) == 10, "All tasks should be claimed once"
    
    @pytest.mark.asyncio
    async def test_agent_isolation(self, redis_client):
        """Verify agents can't interfere with each other"""
        # Create agent with malicious intent (simulated)
        class MaliciousAgent(SecureBaseAgent):
            async def analyze(self, data):
                # Try to access restricted areas
                try:
                    # Attempt to write outside allowed directory
                    with open('/etc/passwd', 'r') as f:
                        f.read()
                    assert False, "Should not be able to read system files"
                except (PermissionError, FileNotFoundError):
                    pass  # Expected
                
                # Try to connect to external network
                import socket
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('google.com', 80))
                    assert False, "Should not have network access"
                except (OSError, socket.error):
                    pass  # Expected
                
                return {'status': 'isolated'}
        
        agent = MaliciousAgent('test', 1)
        result = await agent.analyze("test data")
        assert result['status'] == 'isolated'
```

### Performance Testing

```python
# tests/performance/test_parallel_execution.py

import time
import asyncio
import concurrent.futures
from typing import List

class TestParallelPerformance:
    """Test system performance under load"""
    
    def test_parallel_agent_throughput(self):
        """Measure agent processing throughput"""
        num_agents = 5
        num_tasks = 50
        
        start_time = time.time()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_agents) as executor:
            futures = []
            
            for i in range(num_tasks):
                future = executor.submit(process_transcript, f"transcript_{i}.txt")
                futures.append(future)
            
            # Wait for completion
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = num_tasks / duration
        
        print(f"Processed {num_tasks} tasks in {duration:.2f} seconds")
        print(f"Throughput: {throughput:.2f} tasks/second")
        
        # Performance requirements
        assert throughput > 1.0, "Should process at least 1 task per second"
        assert all(r['success'] for r in results), "All tasks should complete"
    
    def test_orchestrator_failover(self):
        """Test failover between orchestrators"""
        # Start VSCode orchestrator
        vscode_orch = VSCodeOrchestrator()
        vscode_task = asyncio.create_task(vscode_orch.start())
        
        # Process some tasks
        time.sleep(2)
        
        # Simulate VSCode crash
        vscode_orch.running = False
        
        # Start CLI orchestrator
        cli_orch = CLIOrchestrator()
        cli_task = asyncio.create_task(cli_orch.start())
        
        # Verify CLI takes over
        time.sleep(2)
        
        # Check that processing continued
        completed_tasks = redis_client.llen('tasks:completed')
        assert completed_tasks > 0, "CLI should take over processing"
```

### Test Execution Commands

```bash
# Run all tests
make test

# Run specific test categories
make test-unit        # Fast unit tests
make test-integration # Agent communication tests
make test-e2e        # Full pipeline tests
make test-performance # Load and throughput tests

# Run with coverage
make test-coverage

# Run security tests
make test-security
```

---

## 👥 Section 4: Human-in-the-Loop Quality Gates

### Review Interface Architecture

```python
# review_interface/app.py

from flask import Flask, render_template, request, jsonify
import redis
import json
from datetime import datetime

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class ReviewQueue:
    """Manages outputs for human review"""
    
    def __init__(self):
        self.redis = redis_client
    
    def add_for_review(self, output, confidence_score):
        """Add output to review queue with priority"""
        review_item = {
            'id': f"review_{datetime.now().timestamp()}",
            'output': output,
            'confidence': confidence_score,
            'priority': self.calculate_priority(confidence_score),
            'status': 'pending',
            'created': datetime.now().isoformat()
        }
        
        # Add to priority queue (lower confidence = higher priority)
        priority = 100 - int(confidence_score * 100)
        self.redis.zadd(
            'review:queue',
            {json.dumps(review_item): priority}
        )
        
        return review_item['id']
    
    def get_next_for_review(self):
        """Get highest priority item for review"""
        items = self.redis.zrange('review:queue', 0, 0)
        if items:
            item_json = items[0]
            return json.loads(item_json)
        return None
    
    def submit_feedback(self, review_id, decision, feedback):
        """Process human feedback"""
        # Store feedback
        feedback_data = {
            'review_id': review_id,
            'decision': decision,  # 'approve', 'reject', 'revise'
            'feedback': feedback,
            'reviewer': request.remote_addr,  # In production, use auth
            'timestamp': datetime.now().isoformat()
        }
        
        self.redis.hset(
            f'review:feedback:{review_id}',
            mapping=feedback_data
        )
        
        # Learn from feedback
        if decision == 'reject':
            self.learn_from_rejection(review_id, feedback)
        
        return feedback_data

@app.route('/')
def review_dashboard():
    """Main review interface"""
    return render_template('review.html')

@app.route('/api/next-review')
def get_next_review():
    """API endpoint for next item to review"""
    queue = ReviewQueue()
    item = queue.get_next_for_review()
    return jsonify(item)

@app.route('/api/submit-review', methods=['POST'])
def submit_review():
    """API endpoint to submit review feedback"""
    data = request.json
    queue = ReviewQueue()
    result = queue.submit_feedback(
        data['review_id'],
        data['decision'],
        data['feedback']
    )
    return jsonify(result)
```

### Web Interface for Rapid Review

```html
<!-- review_interface/templates/review.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Licia Lab Review Interface</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .review-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .output-panel, .feedback-panel {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            min-height: 400px;
        }
        
        .confidence-indicator {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        .confidence-high { background: #d4edda; color: #155724; }
        .confidence-medium { background: #fff3cd; color: #856404; }
        .confidence-low { background: #f8d7da; color: #721c24; }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .approve { background: #28a745; color: white; }
        .reject { background: #dc3545; color: white; }
        .revise { background: #ffc107; color: black; }
        
        .keyboard-hints {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>📋 Licia Lab Review Interface</h1>
    
    <div class="stats">
        <span id="queue-count">Loading...</span> items in queue |
        <span id="review-rate">0</span> reviews/hour
    </div>
    
    <div class="review-container">
        <div class="output-panel">
            <h3>Output to Review</h3>
            <div class="confidence-indicator" id="confidence">
                Loading...
            </div>
            <div id="output-content">
                Loading next item...
            </div>
        </div>
        
        <div class="feedback-panel">
            <h3>Your Feedback</h3>
            <textarea id="feedback-text" rows="10" style="width: 100%;" 
                placeholder="Enter feedback (optional for approve, required for reject/revise)"></textarea>
            
            <div class="action-buttons">
                <button class="approve" onclick="submitReview('approve')">
                    ✓ Approve (A)
                </button>
                <button class="reject" onclick="submitReview('reject')">
                    ✗ Reject (R)
                </button>
                <button class="revise" onclick="submitReview('revise')">
                    ↻ Revise (V)
                </button>
            </div>
        </div>
    </div>
    
    <div class="keyboard-hints">
        <strong>Keyboard Shortcuts:</strong><br>
        A - Approve | R - Reject | V - Revise | Space - Next
    </div>
    
    <script>
        let currentItem = null;
        
        // Load next item
        async function loadNext() {
            const response = await fetch('/api/next-review');
            currentItem = await response.json();
            
            if (currentItem) {
                document.getElementById('output-content').innerText = 
                    JSON.stringify(currentItem.output, null, 2);
                
                // Update confidence indicator
                const confEl = document.getElementById('confidence');
                const conf = currentItem.confidence;
                confEl.textContent = `Confidence: ${(conf * 100).toFixed(0)}%`;
                confEl.className = 'confidence-indicator ' + 
                    (conf > 0.8 ? 'confidence-high' : 
                     conf > 0.6 ? 'confidence-medium' : 'confidence-low');
                
                // Clear feedback
                document.getElementById('feedback-text').value = '';
            } else {
                document.getElementById('output-content').innerText = 
                    'No items to review!';
            }
        }
        
        // Submit review
        async function submitReview(decision) {
            if (!currentItem) return;
            
            const feedback = document.getElementById('feedback-text').value;
            
            if ((decision === 'reject' || decision === 'revise') && !feedback) {
                alert('Please provide feedback for reject/revise decisions');
                return;
            }
            
            await fetch('/api/submit-review', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    review_id: currentItem.id,
                    decision: decision,
                    feedback: feedback
                })
            });
            
            // Load next
            loadNext();
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            switch(e.key.toLowerCase()) {
                case 'a': submitReview('approve'); break;
                case 'r': submitReview('reject'); break;
                case 'v': submitReview('revise'); break;
                case ' ': e.preventDefault(); loadNext(); break;
            }
        });
        
        // Initial load
        loadNext();
        
        // Update stats
        setInterval(async () => {
            const stats = await fetch('/api/stats').then(r => r.json());
            document.getElementById('queue-count').textContent = stats.queue_count;
            document.getElementById('review-rate').textContent = stats.review_rate;
        }, 5000);
    </script>
</body>
</html>
```

### Quality Scoring System

```python
# quality_gates/scoring.py

class QualityScoring:
    """TDAI (Therapeutic Depth Assessment Index) scoring system"""
    
    def __init__(self):
        self.weights = {
            'emotional_depth': 0.25,
            'somatic_awareness': 0.25,
            'research_integration': 0.20,
            'practical_application': 0.15,
            'cultural_sensitivity': 0.15
        }
    
    def calculate_tdai_score(self, analysis):
        """Calculate comprehensive quality score"""
        scores = {}
        
        # Emotional Depth (0-10)
        scores['emotional_depth'] = self.score_emotional_depth(analysis)
        
        # Somatic Awareness (0-10)
        scores['somatic_awareness'] = self.score_somatic_awareness(analysis)
        
        # Research Integration (0-10)
        scores['research_integration'] = self.score_research_integration(analysis)
        
        # Practical Application (0-10)
        scores['practical_application'] = self.score_practical_application(analysis)
        
        # Cultural Sensitivity (0-10)
        scores['cultural_sensitivity'] = self.score_cultural_sensitivity(analysis)
        
        # Weighted average
        tdai = sum(scores[k] * self.weights[k] for k in scores)
        
        # Confidence based on TDAI
        confidence = tdai / 10.0
        
        return {
            'tdai_score': tdai,
            'confidence': confidence,
            'component_scores': scores,
            'requires_review': tdai < 8.0  # Threshold for human review
        }
    
    def score_emotional_depth(self, analysis):
        """Score emotional nuance and depth"""
        indicators = [
            'micro_expressions' in analysis,
            'emotional_vocabulary' in analysis and len(analysis['emotional_vocabulary']) > 5,
            'feeling_gradients' in analysis,
            'unconscious_patterns' in analysis
        ]
        return sum(indicators) * 2.5
    
    def score_somatic_awareness(self, analysis):
        """Score body awareness and somatic intelligence"""
        indicators = [
            'body_sensations' in analysis,
            'touch_vocabulary' in analysis,
            'movement_patterns' in analysis,
            'breath_awareness' in analysis
        ]
        return sum(indicators) * 2.5
```

---

## 📊 Section 5: Data Ingestion & Vector Database

### Perplexity Thread Ingestion Pipeline

```python
# ingestion/perplexity_processor.py

from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer

class PerplexityProcessor:
    """Process and rank Perplexity research threads"""
    
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(
            name="perplexity_sources",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def ingest_thread(self, html_content: str, thread_id: str) -> Dict:
        """Process a single Perplexity thread"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract sources
        sources = self.extract_sources(soup)
        
        # Rank sources by quality
        ranked_sources = self.rank_sources(sources)
        
        # Extract questions
        questions = self.extract_questions(soup)
        
        # Create synthesis
        synthesis = self.create_weighted_synthesis(ranked_sources, questions)
        
        # Store in vector database
        self.store_in_chromadb(synthesis, thread_id)
        
        return {
            'thread_id': thread_id,
            'total_sources': len(sources),
            'quality_breakdown': self.get_quality_breakdown(ranked_sources),
            'questions': questions,
            'synthesis': synthesis
        }
    
    def extract_sources(self, soup) -> List[Dict]:
        """Extract all sources from Perplexity thread"""
        sources = []
        
        # Find source containers (adjust selectors based on actual HTML)
        source_elements = soup.find_all('div', class_='source-item')
        
        for element in source_elements:
            source = {
                'title': element.find('h3').text if element.find('h3') else '',
                'url': element.find('a')['href'] if element.find('a') else '',
                'snippet': element.find('p').text if element.find('p') else '',
                'author': self.extract_author(element),
                'publication': self.extract_publication(element),
                'date': self.extract_date(element)
            }
            sources.append(source)
        
        return sources
    
    def rank_sources(self, sources: List[Dict]) -> List[Dict]:
        """Rank sources by quality tiers"""
        for source in sources:
            # Tier 1: Academic (score 9-10)
            if any(domain in source['url'] for domain in 
                   ['.edu', 'pubmed', 'scholar', 'arxiv', 'doi.org']):
                source['tier'] = 1
                source['quality_score'] = 9.5
            
            # Tier 2: Professional (score 6-8)
            elif any(domain in source['url'] for domain in 
                     ['.org', '.gov', 'harvard', 'stanford', 'nih']):
                source['tier'] = 2
                source['quality_score'] = 7.0
            
            # Tier 3: General (score 1-5)
            else:
                source['tier'] = 3
                source['quality_score'] = 3.0
            
            # Adjust score based on additional factors
            if source['author'] and 'PhD' in source['author']:
                source['quality_score'] += 1.0
            if source['date'] and self.is_recent(source['date']):
                source['quality_score'] += 0.5
        
        return sorted(sources, key=lambda x: x['quality_score'], reverse=True)
    
    def create_weighted_synthesis(self, sources: List[Dict], questions: List[str]) -> Dict:
        """Create synthesis weighted by source quality"""
        synthesis = {
            'high_confidence_claims': [],  # From Tier 1 sources
            'moderate_confidence_claims': [],  # From Tier 2 sources
            'low_confidence_claims': [],  # From Tier 3 sources
            'questions_addressed': questions,
            'gaps_identified': []
        }
        
        for source in sources:
            claims = self.extract_claims(source['snippet'])
            
            if source['tier'] == 1:
                synthesis['high_confidence_claims'].extend(claims)
            elif source['tier'] == 2:
                synthesis['moderate_confidence_claims'].extend(claims)
            else:
                synthesis['low_confidence_claims'].extend(claims)
        
        # Identify gaps
        synthesis['gaps_identified'] = self.identify_gaps(questions, sources)
        
        return synthesis
    
    def store_in_chromadb(self, synthesis: Dict, thread_id: str):
        """Store processed data in vector database"""
        # Create embeddings for different components
        documents = []
        metadatas = []
        ids = []
        
        # High confidence claims
        for i, claim in enumerate(synthesis['high_confidence_claims']):
            documents.append(claim)
            metadatas.append({
                'thread_id': thread_id,
                'type': 'claim',
                'confidence': 'high',
                'tier': 1
            })
            ids.append(f"{thread_id}_high_{i}")
        
        # Questions
        for i, question in enumerate(synthesis['questions_addressed']):
            documents.append(question)
            metadatas.append({
                'thread_id': thread_id,
                'type': 'question',
                'confidence': 'na',
                'tier': 0
            })
            ids.append(f"{thread_id}_question_{i}")
        
        # Add to ChromaDB
        if documents:
            embeddings = self.embedder.encode(documents).tolist()
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
```

### Vector Database RAG Implementation

```python
# rag/vector_search.py

import chromadb
from typing import List, Dict, Optional
import numpy as np

class VectorRAG:
    """Retrieval-Augmented Generation with ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.Client()
        self.collections = {
            'transcripts': self.client.get_or_create_collection('transcripts'),
            'research': self.client.get_or_create_collection('research'),
            'outputs': self.client.get_or_create_collection('outputs'),
            'perplexity': self.client.get_or_create_collection('perplexity_sources')
        }
        
    def semantic_search(self, query: str, collection: str = 'all', 
                       n_results: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """Perform semantic search across collections"""
        
        if collection == 'all':
            # Search across all collections
            all_results = []
            for coll_name, coll in self.collections.items():
                results = self.search_collection(query, coll, n_results, filters)
                all_results.extend(results)
            
            # Sort by relevance score
            all_results.sort(key=lambda x: x['score'], reverse=True)
            return all_results[:n_results]
        else:
            # Search specific collection
            return self.search_collection(
                query, 
                self.collections[collection], 
                n_results, 
                filters
            )
    
    def search_collection(self, query: str, collection, n_results: int, 
                         filters: Optional[Dict] = None) -> List[Dict]:
        """Search a specific collection"""
        
        # Apply filters if provided
        where_clause = filters if filters else None
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def add_document(self, document: str, metadata: Dict, collection: str = 'outputs'):
        """Add a document to the vector database"""
        
        # Generate unique ID
        doc_id = f"{collection}_{metadata.get('type', 'doc')}_{np.random.randint(1000000)}"
        
        # Add to collection
        self.collections[collection].add(
            documents=[document],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def cross_reference(self, document: str, min_similarity: float = 0.7) -> List[Dict]:
        """Find related content across all collections"""
        
        related = []
        
        for coll_name, collection in self.collections.items():
            results = collection.query(
                query_texts=[document],
                n_results=5
            )
            
            for i in range(len(results['ids'][0])):
                similarity = 1 - results['distances'][0][i]
                if similarity >= min_similarity:
                    related.append({
                        'collection': coll_name,
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': similarity
                    })
        
        return sorted(related, key=lambda x: x['similarity'], reverse=True)
```

### Incremental Indexing System

```python
# rag/incremental_indexing.py

import hashlib
from datetime import datetime
import pickle

class IncrementalIndexer:
    """Efficient incremental indexing without full rebuilds"""
    
    def __init__(self, vector_rag):
        self.rag = vector_rag
        self.index_cache = {}
        self.load_cache()
    
    def add_content(self, content: str, metadata: Dict) -> str:
        """Add new content without reindexing everything"""
        
        # Generate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if already indexed
        if content_hash in self.index_cache:
            return self.index_cache[content_hash]
        
        # Add to vector database
        doc_id = self.rag.add_document(
            content,
            {**metadata, 'indexed_at': datetime.now().isoformat()}
        )
        
        # Update cache
        self.index_cache[content_hash] = doc_id
        self.save_cache()
        
        return doc_id
    
    def batch_add(self, contents: List[Dict]) -> List[str]:
        """Efficiently add multiple documents"""
        doc_ids = []
        
        for item in contents:
            doc_id = self.add_content(item['content'], item['metadata'])
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def update_content(self, doc_id: str, new_content: str, new_metadata: Dict):
        """Update existing content"""
        
        # Remove old version
        # ChromaDB doesn't have direct update, so we delete and re-add
        for collection in self.rag.collections.values():
            try:
                collection.delete(ids=[doc_id])
                break
            except:
                continue
        
        # Add new version
        return self.add_content(new_content, new_metadata)
    
    def save_cache(self):
        """Persist index cache to disk"""
        with open('data/index_cache.pkl', 'wb') as f:
            pickle.dump(self.index_cache, f)
    
    def load_cache(self):
        """Load index cache from disk"""
        try:
            with open('data/index_cache.pkl', 'rb') as f:
                self.index_cache = pickle.load(f)
        except FileNotFoundError:
            self.index_cache = {}
```

---

## 🚀 Quick Commands Reference

### Start Everything
```bash
# One command to rule them all
make rapid-start

# Or step by step:
docker-compose -f docker-compose.secure.yml up -d
python orchestrators/vscode_orchestrator.py &
python orchestrators/cli_orchestrator.py &
python review_interface/app.py &
```

### Process Content
```bash
# Process a transcript
licia-lab process transcript samples/transcript_1.txt

# Ingest Perplexity threads
licia-lab ingest perplexity threads/*.html

# Run full pipeline
licia-lab pipeline --input transcripts/ --output outputs/
```

### Monitor & Debug
```bash
# Check system status
licia-lab status

# View logs
licia-lab logs --orchestrator vscode
licia-lab logs --orchestrator cli
licia-lab logs --agent emotional_nuance

# Security audit
licia-lab security audit

# Performance metrics
licia-lab metrics
```

### Human Review
```bash
# Open review interface
open http://localhost:3000

# Check review queue
licia-lab review status

# Export feedback
licia-lab review export --format csv
```

---

## 📋 Implementation Checklist

### Immediate (Day 1)
- [ ] Run prerequisites check
- [ ] Execute `make rapid-start`
- [ ] Verify all services running
- [ ] Start one orchestrator (VSCode or CLI)
- [ ] Process test transcript
- [ ] Verify output quality

### Day 2
- [ ] Start both orchestrators
- [ ] Test parallel processing
- [ ] Ingest Perplexity threads
- [ ] Set up human review pipeline
- [ ] Process 10 real transcripts

### Day 3
- [ ] Full system test with all agents
- [ ] Performance benchmarking
- [ ] Security audit
- [ ] Generate first editorial materials
- [ ] Train team on review interface

### Week 1
- [ ] Process all available content
- [ ] Refine agent parameters based on feedback
- [ ] Optimize for throughput
- [ ] Create backup and recovery procedures
- [ ] Document team-specific workflows

---

## 🔧 Troubleshooting

### Common Issues

#### "Redis connection refused"
```bash
# Check Redis is running
docker ps | grep redis
# Restart if needed
docker-compose restart redis
```

#### "ChromaDB not responding"
```bash
# Check ChromaDB status
curl http://localhost:8000/api/v1/heartbeat
# Restart if needed
docker-compose restart chromadb
```

#### "Agent timeout"
```bash
# Increase timeout in docker-compose.yml
environment:
  - AGENT_TIMEOUT=60  # Increase from 30
```

#### "Orchestrator conflict"
```bash
# Check active orchestrators
redis-cli keys "orchestrator:*:alive"
# Clear if needed
redis-cli flushdb
```

---

## 🎯 Success Criteria

### System Health
- ✅ All services running without errors
- ✅ Orchestrators cooperating without conflicts
- ✅ Agents processing in parallel
- ✅ Human review pipeline operational
- ✅ Vector database indexing correctly

### Output Quality
- ✅ TDAI scores > 8.0 for most outputs
- ✅ < 20% rejection rate in human review
- ✅ Positive feedback from editorial team
- ✅ Coherent synthesis from Perplexity threads
- ✅ Preserved nuance in emotional analysis

### Performance
- ✅ > 1 transcript/minute throughput
- ✅ < 5 second response time for queries
- ✅ Parallel processing working efficiently
- ✅ No memory leaks or resource exhaustion
- ✅ Automatic failover functioning

---

## 📚 Additional Resources

### Documentation
- Project Documentation: `PROJECT_DOCUMENTATION_V2.md`
- Gap Analysis: `GAP_ANALYSIS.md`
- Editorial Sprint Playbook: `EDITORIAL_SPRINT_PLAYBOOK.md`

### Support
- GitHub Issues: https://github.com/treaties-ai/Licia-Research-Lab-V2/issues
- Internal Slack: #licia-research-lab

### Next Steps
1. After initial setup, review `EDITORIAL_SPRINT_PLAYBOOK.md`
2. Coordinate with editorial team on priorities
3. Schedule daily check-ins during first week
4. Plan for scaling based on initial results

---

*This guide enables rapid deployment of Licia's Research Lab V2 with dual-orchestrator redundancy, secure parallel processing, and human-in-the-loop quality assurance. The system is designed to support the editorial team immediately while maintaining the sophistication needed for this groundbreaking work in trauma healing.*
