"""
Base Orchestrator for Licia's Research Lab V2
Coordinates agent swarms with Redis-based task distribution
"""

import os
import redis
import uuid
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseOrchestrator(ABC):
    """Base class for VSCode and CLI orchestrators"""
    
    def __init__(self, orchestrator_type: str):
        self.orchestrator_type = orchestrator_type
        self.orchestrator_id = f"{orchestrator_type}-{uuid.uuid4().hex[:8]}"
        self.namespace = f"{orchestrator_type}:"
        
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
        # Task queues
        self.pending_queue = "tasks:pending"
        self.processing_queue = f"tasks:processing:{self.orchestrator_id}"
        self.completed_queue = "tasks:completed"
        self.failed_queue = "tasks:failed"
        self.review_queue = "tasks:review"
        
        # Heartbeat settings
        self.heartbeat_interval = 10  # seconds
        self.heartbeat_timeout = 30  # seconds
        self.last_heartbeat = datetime.now()
        
        # Agent registry
        self.agents = {}
        self.agent_waves = {
            1: ['forensic_accuracy', 'verbatim_preservation'],
            2: ['emotional_intelligence', 'somatic_awareness', 'therapeutic_alliance',
                'attachment_dynamics', 'safety_trust', 'unconscious_communication',
                'cultural_context', 'clinical_terminology', 'narrative_coherence',
                'research_connector', 'gaps_identifier'],
            3: ['academic_rigor', 'scientific_validation', 'action_research_validator',
                'semantic_weaponization_detector', 'trauma_pattern_validator'],
            4: ['integration_synthesis']
        }
        
        # Vocabulary synchronization channel
        self.vocab_channel = "vocabulary:updates"
        
        # Thermopylae cross-validation
        self.thermopylae_agents = {
            'detector': 'semantic_weaponization_detector',
            'validator': 'trauma_pattern_validator'
        }
        
        logger.info(f"Initialized {self.orchestrator_type} orchestrator: {self.orchestrator_id}")
    
    async def start(self):
        """Start the orchestrator"""
        logger.info(f"Starting {self.orchestrator_type} orchestrator...")
        
        # Register orchestrator
        await self.register()
        
        # Load agents
        await self.load_agents()
        
        # Start heartbeat
        asyncio.create_task(self.heartbeat_loop())
        
        # Start task processing
        await self.process_tasks()
    
    async def register(self):
        """Register orchestrator in Redis"""
        registration = {
            'id': self.orchestrator_id,
            'type': self.orchestrator_type,
            'started': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Store registration
        self.redis_client.hset(
            f"orchestrators:{self.orchestrator_id}",
            mapping=registration
        )
        
        # Add to active set
        self.redis_client.sadd("orchestrators:active", self.orchestrator_id)
        
        logger.info(f"Registered orchestrator: {self.orchestrator_id}")
    
    async def heartbeat_loop(self):
        """Maintain heartbeat for failover detection"""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            
            # Update heartbeat
            self.redis_client.hset(
                f"orchestrators:{self.orchestrator_id}",
                "last_heartbeat",
                datetime.now().isoformat()
            )
            
            # Check for failed orchestrators
            await self.check_orchestrator_health()
    
    async def check_orchestrator_health(self):
        """Check health of all orchestrators"""
        active_orchestrators = self.redis_client.smembers("orchestrators:active")
        
        for orch_id in active_orchestrators:
            if orch_id == self.orchestrator_id:
                continue
            
            # Get last heartbeat
            last_heartbeat_str = self.redis_client.hget(
                f"orchestrators:{orch_id}",
                "last_heartbeat"
            )
            
            if last_heartbeat_str:
                last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                if datetime.now() - last_heartbeat > timedelta(seconds=self.heartbeat_timeout):
                    logger.warning(f"Orchestrator {orch_id} appears to be down")
                    await self.handle_orchestrator_failure(orch_id)
    
    async def handle_orchestrator_failure(self, failed_orch_id: str):
        """Handle failure of another orchestrator"""
        logger.info(f"Taking over tasks from failed orchestrator: {failed_orch_id}")
        
        # Move tasks from failed orchestrator back to pending
        failed_processing = f"tasks:processing:{failed_orch_id}"
        while True:
            task = self.redis_client.rpoplpush(failed_processing, self.pending_queue)
            if not task:
                break
            logger.info(f"Recovered task: {task[:50]}...")
        
        # Remove from active set
        self.redis_client.srem("orchestrators:active", failed_orch_id)
    
    async def load_agents(self):
        """Load all agents"""
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
        
        for wave_num, agent_names in self.agent_waves.items():
            logger.info(f"Loading Wave {wave_num} agents...")
            for agent_name in agent_names:
                try:
                    # Dynamically import agent module
                    module_name = f"{agent_name}_agent"
                    module = __import__(module_name)
                    
                    # Get agent class
                    class_name = ''.join(w.capitalize() for w in agent_name.split('_')) + 'Agent'
                    agent_class = getattr(module, class_name)
                    
                    # Instantiate agent
                    agent = agent_class()
                    self.agents[agent_name] = agent
                    
                    logger.info(f"  Loaded {agent_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load {agent_name}: {e}")
    
    async def process_tasks(self):
        """Main task processing loop"""
        logger.info("Starting task processing loop...")
        
        while True:
            try:
                # Claim task atomically using RPOPLPUSH
                task_json = self.redis_client.brpoplpush(
                    self.pending_queue,
                    self.processing_queue,
                    timeout=5
                )
                
                if task_json:
                    task = json.loads(task_json)
                    logger.info(f"Processing task: {task.get('id', 'unknown')}")
                    
                    # Process task through agent waves
                    results = await self.process_task_through_waves(task)
                    
                    # Handle results
                    await self.handle_task_results(task, results)
                    
                    # Remove from processing queue
                    self.redis_client.lrem(self.processing_queue, 1, task_json)
                    
            except Exception as e:
                logger.error(f"Error processing task: {e}")
                await asyncio.sleep(1)
    
    async def process_task_through_waves(self, task: Dict) -> Dict:
        """Process task through agent waves"""
        results = {
            'task_id': task.get('id'),
            'timestamp': datetime.now().isoformat(),
            'orchestrator': self.orchestrator_id,
            'waves': {},
            'thermopylae_check': None
        }
        
        transcript = task.get('data', '')
        context = task.get('context', {})
        
        # Process through waves
        for wave_num in sorted(self.agent_waves.keys()):
            wave_results = {}
            
            for agent_name in self.agent_waves[wave_num]:
                if agent_name in self.agents:
                    try:
                        agent = self.agents[agent_name]
                        agent_result = await agent.analyze(transcript, context)
                        wave_results[agent_name] = agent_result
                        
                        # Update context with results for next wave
                        context[f'wave_{wave_num}_{agent_name}'] = agent_result
                        
                    except Exception as e:
                        logger.error(f"Agent {agent_name} failed: {e}")
                        wave_results[agent_name] = {'error': str(e)}
            
            results['waves'][wave_num] = wave_results
        
        # Thermopylae cross-validation
        results['thermopylae_check'] = await self.thermopylae_cross_validation(results)
        
        return results
    
    async def thermopylae_cross_validation(self, results: Dict) -> Dict:
        """Cross-validate semantic weaponization detector and trauma pattern validator"""
        detector_result = results['waves'].get(3, {}).get('semantic_weaponization_detector', {})
        validator_result = results['waves'].get(3, {}).get('trauma_pattern_validator', {})
        
        if not detector_result or not validator_result:
            return {'status': 'incomplete', 'reason': 'Missing agent results'}
        
        # Check for disagreement
        detector_flags = detector_result.get('findings', [])
        validator_confirms = validator_result.get('findings', [])
        
        disagreements = []
        for flag in detector_flags:
            line_num = flag.get('line_number')
            # Check if validator confirmed this as legitimate
            validated = any(v.get('line_number') == line_num for v in validator_confirms)
            if not validated:
                disagreements.append({
                    'line': line_num,
                    'detector_concern': flag.get('category'),
                    'requires_review': True
                })
        
        return {
            'status': 'review_required' if disagreements else 'clear',
            'disagreements': disagreements,
            'checked_at': datetime.now().isoformat()
        }
    
    async def handle_task_results(self, task: Dict, results: Dict):
        """Handle task results"""
        # Calculate TDAI score
        tdai_score = self.calculate_tdai_score(results)
        results['tdai_score'] = tdai_score
        
        # Determine destination based on score and Thermopylae check
        if results['thermopylae_check']['status'] == 'review_required':
            destination = self.review_queue
            logger.info(f"Task {task.get('id')} flagged for Thermopylae review")
        elif tdai_score < 8.0:
            destination = self.review_queue
            logger.info(f"Task {task.get('id')} sent to review (TDAI: {tdai_score:.2f})")
        else:
            destination = self.completed_queue
            logger.info(f"Task {task.get('id')} completed (TDAI: {tdai_score:.2f})")
        
        # Store results
        result_json = json.dumps(results)
        self.redis_client.lpush(destination, result_json)
        
        # Publish to vocabulary updates if high confidence
        if tdai_score >= 8.5:
            await self.publish_vocabulary_updates(results)
    
    def calculate_tdai_score(self, results: Dict) -> float:
        """Calculate Therapeutic Depth Assessment Index score"""
        weights = {
            'emotional_depth': 0.20,
            'somatic_awareness': 0.20,
            'research_integration': 0.15,
            'practical_application': 0.10,
            'cultural_sensitivity': 0.10,
            'forensic_accuracy': 0.15,
            'academic_rigor': 0.10
        }
        
        scores = {
            'emotional_depth': 0.0,
            'somatic_awareness': 0.0,
            'research_integration': 0.0,
            'practical_application': 0.0,
            'cultural_sensitivity': 0.0,
            'forensic_accuracy': 0.0,
            'academic_rigor': 0.0
        }
        
        # Extract scores from agent results
        wave_results = results.get('waves', {})
        
        # Emotional depth from emotional_intelligence
        if 'emotional_intelligence' in wave_results.get(2, {}):
            scores['emotional_depth'] = wave_results[2]['emotional_intelligence'].get('confidence', 0.5) * 10
        
        # Somatic awareness
        if 'somatic_awareness' in wave_results.get(2, {}):
            scores['somatic_awareness'] = wave_results[2]['somatic_awareness'].get('confidence', 0.5) * 10
        
        # Research integration
        if 'research_connector' in wave_results.get(2, {}):
            scores['research_integration'] = wave_results[2]['research_connector'].get('confidence', 0.5) * 10
        
        # Cultural sensitivity
        if 'cultural_context' in wave_results.get(2, {}):
            scores['cultural_sensitivity'] = wave_results[2]['cultural_context'].get('confidence', 0.5) * 10
        
        # Forensic accuracy
        if 'forensic_accuracy' in wave_results.get(1, {}):
            scores['forensic_accuracy'] = wave_results[1]['forensic_accuracy'].get('confidence', 0.5) * 10
        
        # Academic rigor
        if 'academic_rigor' in wave_results.get(3, {}):
            scores['academic_rigor'] = wave_results[3]['academic_rigor'].get('confidence', 0.5) * 10
        
        # Practical application (derived from gaps_identifier)
        if 'gaps_identifier' in wave_results.get(2, {}):
            # Inverse - fewer gaps means better practical application
            gap_count = len(wave_results[2]['gaps_identifier'].get('findings', []))
            scores['practical_application'] = max(0, 10 - gap_count * 0.5)
        
        # Calculate weighted average
        total_score = sum(scores[dim] * weights[dim] for dim in weights)
        
        return min(10.0, total_score)
    
    async def publish_vocabulary_updates(self, results: Dict):
        """Publish vocabulary updates for high-confidence findings"""
        updates = []
        
        for wave_num, wave_results in results.get('waves', {}).items():
            for agent_name, agent_result in wave_results.items():
                patterns = agent_result.get('patterns', [])
                for pattern in patterns:
                    if pattern.get('strength') == 'strong':
                        updates.append({
                            'agent': agent_name,
                            'pattern': pattern.get('pattern'),
                            'frequency': pattern.get('frequency'),
                            'timestamp': datetime.now().isoformat()
                        })
        
        if updates:
            update_msg = json.dumps({
                'orchestrator': self.orchestrator_id,
                'updates': updates
            })
            self.redis_client.publish(self.vocab_channel, update_msg)
            logger.info(f"Published {len(updates)} vocabulary updates")
    
    @abstractmethod
    async def get_auto_approval_settings(self) -> Dict:
        """Get auto-approval settings (implemented by subclasses)"""
        pass
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info(f"Shutting down {self.orchestrator_type} orchestrator...")
        
        # Remove from active set
        self.redis_client.srem("orchestrators:active", self.orchestrator_id)
        
        # Move processing tasks back to pending
        while True:
            task = self.redis_client.rpoplpush(self.processing_queue, self.pending_queue)
            if not task:
                break
        
        logger.info("Orchestrator shutdown complete")
