"""
VSCode Orchestrator for Licia's Research Lab V2
Development-focused orchestrator with auto-approval for safe operations
"""

import asyncio
import logging
from typing import Dict
from base_orchestrator import BaseOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VSCodeOrchestrator(BaseOrchestrator):
    """VSCode-specific orchestrator for development"""
    
    def __init__(self):
        super().__init__("vscode")
        
        # VSCode-specific settings
        self.auto_approve_patterns = {
            'read_operations': True,
            'write_to_outputs': True,
            'write_to_logs': True,
            'redis_operations': False,  # Require approval
            'docker_operations': False,  # Require approval
            'system_commands': False    # Require approval
        }
        
        logger.info("VSCode Orchestrator initialized")
    
    async def get_auto_approval_settings(self) -> Dict:
        """Get VSCode auto-approval settings"""
        return self.auto_approve_patterns
    
    async def process_transcript(self, transcript_path: str):
        """Process a single transcript with development focus"""
        logger.info(f"Processing transcript: {transcript_path}")
        
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = f.read()
        
        # Create task
        import uuid
        import json
        from datetime import datetime
        
        task = {
            'id': str(uuid.uuid4()),
            'type': 'transcript_analysis',
            'source': 'vscode',
            'path': transcript_path,
            'data': transcript_data,
            'context': {
                'orchestrator': 'vscode',
                'development_mode': True,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Add to pending queue
        task_json = json.dumps(task)
        self.redis_client.lpush(self.pending_queue, task_json)
        
        logger.info(f"Task {task['id']} submitted for processing")
        return task['id']
    
    async def monitor_task(self, task_id: str):
        """Monitor task progress with live updates"""
        import json
        
        logger.info(f"Monitoring task: {task_id}")
        
        while True:
            # Check completed queue
            completed = self.redis_client.lrange(self.completed_queue, 0, -1)
            for item in completed:
                result = json.loads(item)
                if result.get('task_id') == task_id:
                    logger.info(f"Task {task_id} completed")
                    logger.info(f"TDAI Score: {result.get('tdai_score', 'N/A'):.2f}")
                    return result
            
            # Check review queue
            review = self.redis_client.lrange(self.review_queue, 0, -1)
            for item in review:
                result = json.loads(item)
                if result.get('task_id') == task_id:
                    logger.info(f"Task {task_id} sent to review")
                    logger.info(f"TDAI Score: {result.get('tdai_score', 'N/A'):.2f}")
                    
                    # Check Thermopylae status
                    thermopylae = result.get('thermopylae_check', {})
                    if thermopylae.get('status') == 'review_required':
                        logger.warning(f"Thermopylae review required: {len(thermopylae.get('disagreements', []))} issues")
                    
                    return result
            
            # Check failed queue
            failed = self.redis_client.lrange(self.failed_queue, 0, -1)
            for item in failed:
                result = json.loads(item)
                if result.get('task_id') == task_id:
                    logger.error(f"Task {task_id} failed")
                    return result
            
            # Wait before checking again
            await asyncio.sleep(2)
    
    async def run_development_mode(self):
        """Run in development mode with enhanced logging"""
        logger.info("Starting VSCode Orchestrator in development mode")
        logger.info("Auto-approval enabled for safe operations")
        logger.info("Manual approval required for: Redis, Docker, System commands")
        
        # Start orchestrator
        await self.start()

def main():
    """Main entry point for VSCode orchestrator"""
    import sys
    
    orchestrator = VSCodeOrchestrator()
    
    if len(sys.argv) > 1:
        # Process specific transcript
        transcript_path = sys.argv[1]
        
        async def process_single():
            task_id = await orchestrator.process_transcript(transcript_path)
            result = await orchestrator.monitor_task(task_id)
            
            # Save result
            import json
            output_path = f"outputs/{task_id}_result.json"
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"Results saved to: {output_path}")
        
        asyncio.run(process_single())
    else:
        # Run continuous processing
        asyncio.run(orchestrator.run_development_mode())

if __name__ == "__main__":
    main()
