"""
CLI Orchestrator for Licia's Research Lab V2
Production-focused orchestrator with parallel worker management
"""

import asyncio
import logging
import argparse
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor
from base_orchestrator import BaseOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLIOrchestrator(BaseOrchestrator):
    """CLI-specific orchestrator for production"""
    
    def __init__(self, num_workers: int = 3):
        super().__init__("cli")
        
        # CLI-specific settings
        self.num_workers = num_workers
        self.auto_approve = False  # Default to manual approval
        self.parallel_mode = True
        
        # Worker pool for parallel processing
        self.worker_pool = None
        
        logger.info(f"CLI Orchestrator initialized with {num_workers} workers")
    
    async def get_auto_approval_settings(self) -> Dict:
        """Get CLI auto-approval settings"""
        return {
            'auto_approve': self.auto_approve,
            'parallel_mode': self.parallel_mode,
            'num_workers': self.num_workers
        }
    
    def set_auto_approve(self, enabled: bool):
        """Enable/disable auto-approval mode"""
        self.auto_approve = enabled
        logger.info(f"Auto-approval mode: {'enabled' if enabled else 'disabled'}")
    
    async def start_workers(self):
        """Start parallel worker processes"""
        if self.parallel_mode:
            self.worker_pool = ProcessPoolExecutor(max_workers=self.num_workers)
            logger.info(f"Started {self.num_workers} worker processes")
    
    async def process_batch(self, transcript_paths: List[str]):
        """Process multiple transcripts in parallel"""
        import uuid
        import json
        from datetime import datetime
        
        logger.info(f"Processing batch of {len(transcript_paths)} transcripts")
        
        tasks = []
        for path in transcript_paths:
            # Read transcript
            with open(path, 'r', encoding='utf-8') as f:
                transcript_data = f.read()
            
            # Create task
            task = {
                'id': str(uuid.uuid4()),
                'type': 'transcript_analysis',
                'source': 'cli',
                'path': path,
                'data': transcript_data,
                'context': {
                    'orchestrator': 'cli',
                    'production_mode': True,
                    'auto_approve': self.auto_approve,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            tasks.append(task)
        
        # Submit all tasks to queue
        for task in tasks:
            task_json = json.dumps(task)
            self.redis_client.lpush(self.pending_queue, task_json)
            logger.info(f"Task {task['id']} submitted")
        
        # Return task IDs for monitoring
        return [task['id'] for task in tasks]
    
    async def monitor_batch(self, task_ids: List[str]):
        """Monitor batch processing progress"""
        import json
        from datetime import datetime
        
        completed = set()
        review = set()
        failed = set()
        
        start_time = datetime.now()
        
        while len(completed) + len(review) + len(failed) < len(task_ids):
            # Check all queues
            for queue_name, status_set in [
                (self.completed_queue, completed),
                (self.review_queue, review),
                (self.failed_queue, failed)
            ]:
                items = self.redis_client.lrange(queue_name, 0, -1)
                for item in items:
                    result = json.loads(item)
                    task_id = result.get('task_id')
                    if task_id in task_ids and task_id not in status_set:
                        status_set.add(task_id)
                        
                        # Log status
                        if queue_name == self.completed_queue:
                            tdai = result.get('tdai_score', 0)
                            logger.info(f"✅ Task {task_id[:8]}... completed (TDAI: {tdai:.2f})")
                        elif queue_name == self.review_queue:
                            tdai = result.get('tdai_score', 0)
                            thermopylae = result.get('thermopylae_check', {})
                            if thermopylae.get('status') == 'review_required':
                                logger.warning(f"⚠️  Task {task_id[:8]}... needs Thermopylae review")
                            else:
                                logger.info(f"📝 Task {task_id[:8]}... sent to review (TDAI: {tdai:.2f})")
                        else:
                            logger.error(f"❌ Task {task_id[:8]}... failed")
            
            # Progress update
            total = len(task_ids)
            done = len(completed) + len(review) + len(failed)
            if done > 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = done / elapsed
                eta = (total - done) / rate if rate > 0 else 0
                
                print(f"\rProgress: {done}/{total} ({done*100/total:.1f}%) | "
                      f"Rate: {rate:.2f} tasks/sec | ETA: {eta:.0f}s", end='')
            
            await asyncio.sleep(1)
        
        print()  # New line after progress
        
        # Final summary
        logger.info("=" * 50)
        logger.info("Batch Processing Complete")
        logger.info(f"  Completed: {len(completed)}")
        logger.info(f"  Review: {len(review)}")
        logger.info(f"  Failed: {len(failed)}")
        logger.info(f"  Total time: {(datetime.now() - start_time).total_seconds():.1f}s")
        logger.info("=" * 50)
        
        return {
            'completed': list(completed),
            'review': list(review),
            'failed': list(failed)
        }
    
    async def export_results(self, task_ids: List[str], output_dir: str = "outputs"):
        """Export results to files"""
        import json
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = os.path.join(output_dir, f"batch_{timestamp}")
        os.makedirs(batch_dir, exist_ok=True)
        
        # Export individual results
        for task_id in task_ids:
            # Check all queues for result
            for queue_name in [self.completed_queue, self.review_queue, self.failed_queue]:
                items = self.redis_client.lrange(queue_name, 0, -1)
                for item in items:
                    result = json.loads(item)
                    if result.get('task_id') == task_id:
                        # Save result
                        output_path = os.path.join(batch_dir, f"{task_id}.json")
                        with open(output_path, 'w') as f:
                            json.dump(result, f, indent=2)
                        break
        
        # Create summary
        summary_path = os.path.join(batch_dir, "summary.json")
        summary = {
            'timestamp': timestamp,
            'total_tasks': len(task_ids),
            'task_ids': task_ids,
            'output_directory': batch_dir
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Results exported to: {batch_dir}")
        return batch_dir
    
    async def run_production_mode(self):
        """Run in production mode with parallel processing"""
        logger.info("Starting CLI Orchestrator in production mode")
        logger.info(f"Parallel processing: {self.num_workers} workers")
        logger.info(f"Auto-approval: {'enabled' if self.auto_approve else 'disabled'}")
        
        # Start workers
        await self.start_workers()
        
        # Start orchestrator
        await self.start()

def main():
    """Main entry point for CLI orchestrator"""
    parser = argparse.ArgumentParser(description='Licia Research Lab CLI Orchestrator')
    parser.add_argument('--workers', type=int, default=3,
                        help='Number of parallel workers (default: 3)')
    parser.add_argument('--auto-approve', action='store_true',
                        help='Enable auto-approval mode')
    parser.add_argument('--batch', nargs='+',
                        help='Process batch of transcript files')
    parser.add_argument('--export', action='store_true',
                        help='Export results after processing')
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = CLIOrchestrator(num_workers=args.workers)
    
    if args.auto_approve:
        orchestrator.set_auto_approve(True)
    
    if args.batch:
        # Process batch
        async def process_batch():
            # Start workers
            await orchestrator.start_workers()
            
            # Process transcripts
            task_ids = await orchestrator.process_batch(args.batch)
            
            # Monitor progress
            results = await orchestrator.monitor_batch(task_ids)
            
            # Export if requested
            if args.export:
                await orchestrator.export_results(task_ids)
            
            # Shutdown
            await orchestrator.shutdown()
        
        asyncio.run(process_batch())
    else:
        # Run continuous processing
        asyncio.run(orchestrator.run_production_mode())

if __name__ == "__main__":
    main()
