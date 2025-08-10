#!/usr/bin/env python3
"""
Bootstrap script to extract code from RAPID_IMPLEMENTATION_GUIDE.md
and create actual implementation files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def extract_code_blocks(markdown_file: str) -> List[Tuple[str, str, str]]:
    """
    Extract code blocks from markdown file.
    Returns list of (language, filepath, code) tuples.
    """
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Pattern to match code blocks with file paths in comments
    pattern = r'```(\w+)\s*\n#\s*([^\n]+\.(?:py|yml|yaml|json|html|css|js))\s*\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    code_blocks = []
    for lang, filepath, code in matches:
        # Clean up the filepath
        filepath = filepath.strip()
        if filepath.startswith('#'):
            filepath = filepath[1:].strip()
        code_blocks.append((lang, filepath, code))
    
    return code_blocks

def create_file_from_block(filepath: str, code: str):
    """Create a file with the extracted code."""
    # Create directory if it doesn't exist
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the code to file
    with open(path, 'w') as f:
        f.write(code)
    
    print(f"✅ Created: {filepath}")

def extract_specific_implementations():
    """Extract specific implementations mentioned in the guide."""
    
    # Map of section markers to file paths
    implementations = {
        'orchestrators/vscode_orchestrator.py': '''import redis
import uuid
from datetime import datetime
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"🚀 VSCode Orchestrator started: {self.orchestrator_id}")
        
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
        logger.info(f"📋 VSCode executing task: {task['id']}")
        
        try:
            # Dispatch to appropriate agent
            if task.get('type') == 'transcript':
                await self.process_transcript(task)
            elif task.get('type') == 'perplexity':
                await self.process_perplexity(task)
            elif task.get('type') == 'synthesis':
                await self.process_synthesis(task)
            
            # Mark complete
            self.complete_task(task)
            
        except Exception as e:
            self.handle_task_error(task, e)
    
    async def process_transcript(self, task):
        """Process a transcript task"""
        logger.info(f"Processing transcript: {task.get('data', 'unknown')}")
        # Placeholder for actual processing
        await asyncio.sleep(2)
        
    async def process_perplexity(self, task):
        """Process a Perplexity thread"""
        logger.info(f"Processing Perplexity thread: {task.get('data', 'unknown')}")
        # Placeholder for actual processing
        await asyncio.sleep(2)
        
    async def process_synthesis(self, task):
        """Process a synthesis task"""
        logger.info(f"Processing synthesis: {task.get('data', 'unknown')}")
        # Placeholder for actual processing
        await asyncio.sleep(2)
    
    def complete_task(self, task):
        """Mark a task as complete"""
        self.redis_client.hset(f"task:{task['id']}", "status", "completed")
        self.redis_client.lpush("tasks:completed", task['id'])
        logger.info(f"✅ Task completed: {task['id']}")
    
    def handle_task_error(self, task, error):
        """Handle task processing errors"""
        logger.error(f"❌ Task {task['id']} failed: {error}")
        self.redis_client.hset(f"task:{task['id']}", "status", "failed")
        self.redis_client.hset(f"task:{task['id']}", "error", str(error))

if __name__ == "__main__":
    orchestrator = VSCodeOrchestrator()
    
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        logger.info("Shutting down VSCode orchestrator...")
        orchestrator.running = False
''',
        
        'orchestrators/cli_orchestrator.py': '''import click
import redis
import uuid
from datetime import datetime
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        click.echo(f"📋 CLI executing task: {task['id']}")
        
        try:
            # Dispatch to appropriate agent
            if task.get('type') == 'transcript':
                await self.process_transcript(task)
            elif task.get('type') == 'perplexity':
                await self.process_perplexity(task)
            elif task.get('type') == 'synthesis':
                await self.process_synthesis(task)
            
            # Mark complete
            self.complete_task(task)
            
        except Exception as e:
            self.handle_task_error(task, e)
    
    async def process_transcript(self, task):
        """Process a transcript task"""
        click.echo(f"Processing transcript: {task.get('data', 'unknown')}")
        # Placeholder for actual processing
        await asyncio.sleep(2)
        
    async def process_perplexity(self, task):
        """Process a Perplexity thread"""
        click.echo(f"Processing Perplexity thread: {task.get('data', 'unknown')}")
        # Placeholder for actual processing
        await asyncio.sleep(2)
        
    async def process_synthesis(self, task):
        """Process a synthesis task"""
        click.echo(f"Processing synthesis: {task.get('data', 'unknown')}")
        # Placeholder for actual processing
        await asyncio.sleep(2)
    
    def complete_task(self, task):
        """Mark a task as complete"""
        self.redis_client.hset(f"task:{task['id']}", "status", "completed")
        self.redis_client.lpush("tasks:completed", task['id'])
        click.echo(click.style(f"✅ Task completed: {task['id']}", fg='green'))
    
    def handle_task_error(self, task, error):
        """Handle task processing errors"""
        click.echo(click.style(f"❌ Task {task['id']} failed: {error}", fg='red'))
        self.redis_client.hset(f"task:{task['id']}", "status", "failed")
        self.redis_client.hset(f"task:{task['id']}", "error", str(error))

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
    
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        click.echo("\\nShutting down CLI orchestrator...")
        orchestrator.running = False

if __name__ == '__main__':
    start_cli_orchestrator()
'''
    }
    
    # Create each file
    for filepath, code in implementations.items():
        create_file_from_block(filepath, code)

def main():
    """Main bootstrap function"""
    print("🚀 Starting bootstrap process...")
    print("=" * 50)
    
    # Check if guide exists
    guide_path = "RAPID_IMPLEMENTATION_GUIDE.md"
    if not os.path.exists(guide_path):
        print("❌ RAPID_IMPLEMENTATION_GUIDE.md not found!")
        return
    
    # Extract code blocks
    print("📖 Reading implementation guide...")
    code_blocks = extract_code_blocks(guide_path)
    print(f"Found {len(code_blocks)} code blocks")
    
    # Create files from code blocks
    for lang, filepath, code in code_blocks:
        if filepath and not filepath.startswith('//'):
            create_file_from_block(filepath, code)
    
    # Extract specific implementations
    print("\n📦 Creating core implementation files...")
    extract_specific_implementations()
    
    print("\n✅ Bootstrap complete!")
    print("Next steps:")
    print("1. Run 'make install-deps' to install Python dependencies")
    print("2. Run 'make rapid-start' to launch the system")
    print("3. Access review interface at http://localhost:3000")

if __name__ == "__main__":
    main()
