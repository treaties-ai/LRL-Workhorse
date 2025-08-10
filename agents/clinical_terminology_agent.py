"""
ClinicalTerminologyAgent - Maintains dual vocabularies for different audiences
Part of Licia's Research Lab V2
Wave 2 Agent - Tier 2 Security
"""

import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from base_agent import BaseAgent

class ClinicalTerminologyAgent(BaseAgent):
    """
    Maintains dual vocabularies for different audiences
    
    Action Research Paradigm:
    - Documents what works in practice
    - Finds science to explain observed outcomes
    - Validates through systematic observation
    """
    
    def __init__(self):
        super().__init__("clinical_terminology", permission_tier=2)
        
        # Specialized vocabulary for clinical_terminology
        self.vocabulary = {
            "technical": [
                        "DSM-5",
                        "ICD-11",
                        "diagnosis",
                        "symptomatology"
            ],
            "accessible": [
                        "struggle",
                        "difficulty",
                        "pattern",
                        "experience"
            ],
            "bridge": [
                        "translation",
                        "explanation",
                        "clarification",
                        "simplification"
            ],
            "precision": [
                        "operationalized",
                        "measurable",
                        "criteria",
                        "threshold"
            ]
}
        
        # Action research tracking
        self.practice_observations = []
        self.pattern_tracker = {}
        
    async def analyze(self, data: str, context: Dict = None) -> Dict[str, Any]:
        """
        Analyze transcript for clinical terminology patterns
        
        Action Research Approach:
        1. Document what happens in practice
        2. Identify emergent patterns
        3. Find scientific explanations
        """
        # Security validation first
        clean_data = self.validate_input(data)
        
        # Initialize results
        results = {
            'agent': self.agent_type,
            'timestamp': datetime.now().isoformat(),
            'methodology': 'action_research',
            'findings': [],
            'patterns': [],
            'confidence': 0.0
        }
        
        # Perform specialized analysis
        findings = self._analyze_clinical_terminology(clean_data, context)
        results['findings'] = findings
        
        # Track patterns for action research
        self._track_patterns(findings)
        results['patterns'] = self._identify_patterns()
        
        # Calculate confidence
        results['confidence'] = self._calculate_confidence(findings)
        
        # Save to memory
        self.save_to_memory(results, {
            'data_length': len(clean_data),
            'context': context or {},
            'wave': 2
        })
        
        # Sign output
        results['signature'] = self.sign_output(results)
        
        return results
    
    def _analyze_clinical_terminology(self, data: str, context: Dict = None) -> List[Dict]:
        """Specialized analysis for clinical terminology"""
        findings = []
        lines = data.split('\n')
        
        # Search for vocabulary patterns
        for vocab_category, terms in self.vocabulary.items():
            for i, line in enumerate(lines):
                lower_line = line.lower()
                for term in terms:
                    if term.lower() in lower_line:
                        findings.append({
                            'line_number': i + 1,
                            'category': vocab_category,
                            'term': term,
                            'context': line.strip(),
                            'confidence': self._assess_confidence(term, line)
                        })
        
        return findings
    
    def _track_patterns(self, findings: List[Dict]):
        """Track patterns for action research methodology"""
        for finding in findings:
            pattern_key = f"{finding['category']}:{finding['term']}"
            if pattern_key not in self.pattern_tracker:
                self.pattern_tracker[pattern_key] = {
                    'count': 0,
                    'contexts': [],
                    'first_seen': datetime.now().isoformat()
                }
            
            self.pattern_tracker[pattern_key]['count'] += 1
            self.pattern_tracker[pattern_key]['contexts'].append(finding['context'])
    
    def _identify_patterns(self) -> List[Dict]:
        """Identify emergent patterns (inductive approach)"""
        patterns = []
        
        for pattern_key, data in self.pattern_tracker.items():
            if data['count'] >= 3:  # Pattern threshold
                patterns.append({
                    'pattern': pattern_key,
                    'frequency': data['count'],
                    'strength': 'strong' if data['count'] >= 5 else 'moderate',
                    'action_research_note': 'Pattern emerged from practice observation'
                })
        
        return patterns
    
    def _assess_confidence(self, term: str, context: str) -> float:
        """Assess confidence in finding"""
        # Higher confidence for clear, unambiguous matches
        confidence = 0.7  # Base confidence
        
        # Adjust based on context clarity
        if term == context.strip():
            confidence = 1.0  # Exact match
        elif len(context.split()) < 10:
            confidence = 0.8  # Short, clear context
        
        return confidence
    
    def _calculate_confidence(self, findings: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not findings:
            return 0.0
        
        # Average confidence of all findings
        total_confidence = sum(f.get('confidence', 0.5) for f in findings)
        avg_confidence = total_confidence / len(findings)
        
        # Boost for pattern consistency
        pattern_boost = min(0.2, len(self.pattern_tracker) * 0.02)
        
        return min(1.0, avg_confidence + pattern_boost)
