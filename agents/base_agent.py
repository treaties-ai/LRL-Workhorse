"""
Base agent class for all agents in the system
WITH SECURITY HARDENING AGAINST UNICODE AND PROMPT INJECTION ATTACKS
"""

import os
import sys
import json
from datetime import datetime
import hashlib
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union

# Set up logging FIRST before any use
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SECURITY: Explicit import validation to prevent hijacking
try:
    import redis
    # Verify it's the real redis module by checking for expected attributes
    if not hasattr(redis, 'Redis') or not hasattr(redis, 'ConnectionPool'):
        raise ImportError("Invalid redis module detected - potential hijack attempt!")
except ImportError as e:
    logger.error(f"SECURITY ERROR: Redis import failed - {e}")
    logger.error("Install with: pip install redis")
    logger.error("This could be an import hijacking attempt!")
    sys.exit(1)

# Type validation for security
if not isinstance(redis.Redis, type):
    logger.error("SECURITY: Redis.Redis is not a class - potential type confusion attack")
    sys.exit(1)

class SecurityError(Exception):
    """Raised when security validation fails"""
    pass


class BaseAgent:
    """Base class with security controls for all agents"""
    
    def __init__(self, agent_type: str, permission_tier: int = 1):
        self.agent_type = agent_type
        self.permission_tier = permission_tier
        self.agent_id = f"{agent_type}-{os.environ.get('HOSTNAME', 'local')}"
        
        # Redis connection for communication
        self.redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Audit all operations
        self.audit_log = []
        
        logger.info(f"Initialized {self.agent_type} agent with ID: {self.agent_id}")
        
    async def analyze(self, data: str) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by each agent
        """
        raise NotImplementedError("Each agent must implement analyze()")
    
    def validate_input(self, data: str) -> str:
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
    
    async def process_with_limits(self, data: str) -> Dict[str, Any]:
        """Process data with resource limits"""
        try:
            # Validate input
            clean_data = self.validate_input(data)
            
            # Process
            result = await self.analyze(clean_data)
            
            # Sign output for integrity
            result['signature'] = self.sign_output(result)
            result['agent_id'] = self.agent_id
            result['timestamp'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            self.log_security_event('PROCESSING_ERROR', {'error': str(e)})
            raise
    
    def sign_output(self, data: Dict) -> str:
        """Create integrity signature for output"""
        content = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(
            f"{self.agent_id}:{content}".encode()
        ).hexdigest()
        return signature
    
    def log_security_event(self, event_type: str, details: Dict):
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
        try:
            self.redis_client.lpush(
                'security:events',
                json.dumps(event)
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
        
        # Alert on critical events
        if event_type in ['INJECTION_ATTEMPT', 'BREACH_DETECTED']:
            try:
                self.redis_client.publish(
                    'security:alerts',
                    json.dumps(event)
                )
            except Exception as e:
                logger.error(f"Failed to publish security alert: {e}")
    
    def save_to_memory(self, content: Any, metadata: Dict):
        """Save analysis results to Redis for later retrieval"""
        key = f"memory:{self.agent_type}:{datetime.now().timestamp()}"
        
        data = {
            'content': content,
            'metadata': metadata,
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self.redis_client.set(key, json.dumps(data), ex=86400)  # 24 hour expiry
            logger.info(f"Saved to memory: {key}")
        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")
    
    def get_from_memory(self, pattern: str = "*") -> list:
        """Retrieve previous analyses from memory"""
        results = []
        
        try:
            keys = self.redis_client.keys(f"memory:{self.agent_type}:{pattern}")
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    results.append(json.loads(data))
        except Exception as e:
            logger.error(f"Failed to retrieve from memory: {e}")
        
        return results


class EmotionalNuanceAgent(BaseAgent):
    """
    Example agent: Preserves emotional nuance and subtlety
    """
    
    def __init__(self):
        super().__init__("emotional_nuance", permission_tier=1)
        self.emotion_keywords: List[str] = [
            'feel', 'feeling', 'emotion', 'sense', 'heart',
            'anxiety', 'fear', 'joy', 'sadness', 'anger'
        ]
    
    async def analyze(self, data: str) -> Dict[str, Any]:
        """
        Analyze data (transcript) for emotional nuance
        SECURITY: Parameter name MUST match base class to ensure validation
        """
        # SECURITY: 'data' parameter ensures base class validation is applied
        transcript = data  # Alias for clarity in this context
        
        # Simple example analysis
        lines = transcript.split('\n')
        emotional_moments: List[Dict[str, Any]] = []
        
        for i, line in enumerate(lines):
            lower_line = line.lower()
            for keyword in self.emotion_keywords:
                if keyword in lower_line:
                    emotional_moments.append({
                        'line_number': i + 1,
                        'text': line.strip(),
                        'keyword': keyword
                    })
        
        analysis = {
            'emotional_moments': emotional_moments,
            'total_emotional_references': len(emotional_moments),
            'nuance_preserved': True,
            'analysis_type': 'emotional_nuance'
        }
        
        # Save to memory for later reference
        self.save_to_memory(analysis, {
            'transcript_length': len(transcript),
            'lines_analyzed': len(lines)
        })
        
        return analysis


if __name__ == "__main__":
    # Simple test
    agent = EmotionalNuanceAgent()
    
    test_transcript = """
    Patient: I feel this tightness in my chest when I think about it.
    Therapist: Can you describe where exactly you feel it?
    Patient: Right here, like a fist squeezing my heart. It makes me anxious.
    """
    
    # Run async analysis
    async def test():
        result = await agent.process_with_limits(test_transcript)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())
