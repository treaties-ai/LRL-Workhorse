"""
Agent Factory for Licia's Research Lab V2
Generates all 18 specialized agents with action research paradigm
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
import asyncio
from concurrent.futures import ProcessPoolExecutor
from base_agent import BaseAgent

class AgentFactory:
    """Factory for generating all 18 agents in parallel"""
    
    AGENT_SPECIFICATIONS = {
        # Wave 1: Forensic Foundation
        'forensic_accuracy': {
            'tier': 1,
            'wave': 1,
            'description': 'Character-by-character transcript validation',
            'vocabulary': {
                'verification': ['checksum', 'hash', 'immutable', 'audit_trail'],
                'accuracy': ['verbatim', 'unaltered', 'original', 'preserved'],
                'forensic': ['chain_of_custody', 'integrity', 'validation']
            }
        },
        'verbatim_preservation': {
            'tier': 1,
            'wave': 1,
            'description': 'Maintains exact transcript fidelity',
            'vocabulary': {
                'preservation': ['exact_quote', 'hesitation', 'pause', 'filler'],
                'fidelity': ['unmodified', 'precise', 'literal', 'accurate'],
                'markers': ['um', 'uh', 'silence', 'breath']
            }
        },
        
        # Wave 2: Core Analysis
        'emotional_intelligence': {
            'tier': 2,
            'wave': 2,
            'description': 'Tracks emotional progressions and patterns',
            'vocabulary': {
                'regulation': ['self-soothing', 'co-regulation', 'dysregulation'],
                'tolerance': ['affect_tolerance', 'window_of_tolerance', 'hyper/hypoarousal'],
                'integration': ['emotional_integration', 'split_affects', 'ambivalence'],
                'progression': ['emotional_arc', 'feeling_evolution', 'affect_shift']
            }
        },
        'somatic_awareness': {
            'tier': 2,
            'wave': 2,
            'description': 'Maps body sensations to emotional states',
            'vocabulary': {
                'sensations': ['tightness', 'heaviness', 'warmth', 'tingling', 'numbness', 'constriction'],
                'processes': ['titration', 'pendulation', 'discharge', 'completion', 'resourcing'],
                'awareness': ['interoception', 'neuroception', 'felt_sense', 'body_scan'],
                'somatic_markers': ['breath_pattern', 'muscle_tension', 'temperature', 'movement']
            }
        },
        'therapeutic_alliance': {
            'tier': 2,
            'wave': 2,
            'description': 'Measures trust and relational dynamics',
            'vocabulary': {
                'trust': ['safety', 'rapport', 'attunement', 'resonance'],
                'dynamics': ['transference', 'countertransference', 'enactment', 'rupture'],
                'repair': ['reconnection', 'restoration', 'mending', 'healing'],
                'indicators': ['eye_contact', 'body_language', 'voice_tone', 'engagement']
            }
        },
        'attachment_dynamics': {
            'tier': 2,
            'wave': 2,
            'description': 'Identifies attachment patterns and styles',
            'vocabulary': {
                'styles': ['secure', 'anxious', 'avoidant', 'disorganized'],
                'patterns': ['proximity_seeking', 'safe_haven', 'secure_base', 'separation_distress'],
                'dynamics': ['activation', 'deactivation', 'hyperactivation', 'earned_security'],
                'markers': ['dependency', 'autonomy', 'intimacy', 'distance']
            }
        },
        'safety_trust': {
            'tier': 2,
            'wave': 2,
            'description': 'Detects psychological safety markers',
            'vocabulary': {
                'safety': ['containment', 'boundaries', 'predictability', 'stability'],
                'trust': ['reliability', 'consistency', 'transparency', 'vulnerability'],
                'indicators': ['disclosure', 'openness', 'risk_taking', 'exploration'],
                'threat': ['hypervigilance', 'scanning', 'bracing', 'withdrawal']
            }
        },
        'unconscious_communication': {
            'tier': 2,
            'wave': 2,
            'description': 'Captures non-verbal and implicit patterns',
            'vocabulary': {
                'nonverbal': ['pause', 'sigh', 'gesture', 'posture', 'facial_expression'],
                'implicit': ['metaphor', 'symbol', 'dream', 'slip', 'association'],
                'patterns': ['repetition', 'omission', 'emphasis', 'rhythm'],
                'process': ['enactment', 'projection', 'unconscious_fantasy']
            }
        },
        'cultural_context': {
            'tier': 2,
            'wave': 2,
            'description': 'Respects diverse healing traditions',
            'vocabulary': {
                'traditions': ['indigenous', 'ancestral', 'cultural', 'spiritual'],
                'practices': ['ritual', 'ceremony', 'community', 'collective'],
                'wisdom': ['elder', 'lineage', 'transmission', 'oral_tradition'],
                'respect': ['cultural_humility', 'non_appropriation', 'honoring']
            }
        },
        'clinical_terminology': {
            'tier': 2,
            'wave': 2,
            'description': 'Maintains dual vocabularies for different audiences',
            'vocabulary': {
                'technical': ['DSM-5', 'ICD-11', 'diagnosis', 'symptomatology'],
                'accessible': ['struggle', 'difficulty', 'pattern', 'experience'],
                'bridge': ['translation', 'explanation', 'clarification', 'simplification'],
                'precision': ['operationalized', 'measurable', 'criteria', 'threshold']
            }
        },
        'narrative_coherence': {
            'tier': 2,
            'wave': 2,
            'description': 'Tracks story structure and flow',
            'vocabulary': {
                'structure': ['beginning', 'middle', 'end', 'arc', 'trajectory'],
                'coherence': ['continuity', 'consistency', 'integration', 'flow'],
                'disruption': ['fragmentation', 'dissociation', 'gaps', 'confusion'],
                'repair': ['weaving', 'connecting', 'bridging', 'integrating']
            }
        },
        'research_connector': {
            'tier': 2,
            'wave': 2,
            'description': 'Links practice to supporting research',
            'vocabulary': {
                'evidence': ['study', 'research', 'finding', 'data'],
                'quality': ['peer_reviewed', 'RCT', 'meta_analysis', 'systematic_review'],
                'connection': ['supports', 'validates', 'explains', 'corroborates'],
                'action_research': ['practice_based', 'inductive', 'emergent', 'grounded']
            }
        },
        'gaps_identifier': {
            'tier': 2,
            'wave': 2,
            'description': 'Finds missing therapeutic elements',
            'vocabulary': {
                'missing': ['absence', 'void', 'gap', 'omission'],
                'needed': ['required', 'essential', 'critical', 'important'],
                'patterns': ['consistent_absence', 'recurring_gap', 'systematic_omission'],
                'opportunity': ['potential', 'possibility', 'opening', 'space']
            }
        },
        
        # Wave 3: Validation & Security
        'academic_rigor': {
            'tier': 3,
            'wave': 3,
            'description': 'Ensures academic standards with action research focus',
            'vocabulary': {
                'methodology': ['action_research', 'inductive', 'grounded_theory', 'phenomenological'],
                'rigor': ['systematic', 'transparent', 'replicable', 'trustworthy'],
                'evidence': ['triangulation', 'saturation', 'member_checking', 'audit_trail'],
                'ethics': ['beneficence', 'non_maleficence', 'autonomy', 'justice']
            }
        },
        'scientific_validation': {
            'tier': 3,
            'wave': 3,
            'description': 'Validates through practice-to-theory approach',
            'vocabulary': {
                'validation': ['empirical', 'observable', 'measurable', 'verifiable'],
                'methodology': ['inductive', 'emergent', 'iterative', 'reflexive'],
                'strength': ['convergent', 'divergent', 'explanatory', 'predictive'],
                'practice_based': ['clinical_outcomes', 'therapeutic_results', 'lived_experience']
            }
        },
        'action_research_validator': {
            'tier': 3,
            'wave': 3,
            'description': 'Ensures proper action research methodology',
            'vocabulary': {
                'action_research': ['practice_to_theory', 'wisdom_validating', 'outcome_based'],
                'inductive': ['pattern_emergence', 'bottom_up', 'grounded', 'emergent'],
                'systematic': ['documentation', 'observation', 'reflection', 'iteration'],
                'ethics': ['participant_centered', 'collaborative', 'transformative']
            }
        },
        'semantic_weaponization_detector': {
            'tier': 3,
            'wave': 3,
            'description': 'Detects attacks hidden in therapeutic language',
            'vocabulary': {
                'attack_patterns': ['command_syntax', 'directive_language', 'injection_attempt'],
                'therapeutic_overlap': ['ignore_pain', 'ignore_signals', 'disregard_feelings'],
                'detection': ['context_analysis', 'syntax_checking', 'pattern_matching'],
                'thermopylae': ['gateway', 'vulnerability', 'dual_use', 'boundary']
            }
        },
        'trauma_pattern_validator': {
            'tier': 3,
            'wave': 3,
            'description': 'Confirms legitimate therapeutic content',
            'vocabulary': {
                'trauma_patterns': ['avoidance', 'intrusion', 'hyperarousal', 'dissociation'],
                'therapeutic': ['processing', 'integration', 'resolution', 'healing'],
                'validation': ['authentic', 'legitimate', 'clinical', 'therapeutic'],
                'markers': ['narrative_flow', 'emotional_congruence', 'somatic_alignment']
            }
        },
        
        # Wave 4: Synthesis
        'integration_synthesis': {
            'tier': 3,
            'wave': 4,
            'description': 'Combines outputs from all agents',
            'vocabulary': {
                'integration': ['synthesis', 'combination', 'weaving', 'merging'],
                'holistic': ['comprehensive', 'complete', 'unified', 'integrated'],
                'patterns': ['convergence', 'divergence', 'themes', 'threads'],
                'output': ['summary', 'findings', 'insights', 'recommendations']
            }
        }
    }
    
    @classmethod
    async def create_all_agents(cls) -> Dict[str, Any]:
        """Create all agents in parallel"""
        agents = {}
        tasks = []
        
        # Create agents asynchronously
        for agent_name, spec in cls.AGENT_SPECIFICATIONS.items():
            task = asyncio.create_task(cls._create_agent(agent_name, spec))
            tasks.append(task)
        
        # Wait for all agents to be created
        results = await asyncio.gather(*tasks)
        
        # Organize by wave
        waves = {1: [], 2: [], 3: [], 4: []}
        for agent_name, agent_obj in results:
            wave = cls.AGENT_SPECIFICATIONS[agent_name]['wave']
            waves[wave].append((agent_name, agent_obj))
            agents[agent_name] = agent_obj
        
        print(f"✅ Created {len(agents)} agents in 4 waves")
        for wave_num, wave_agents in waves.items():
            print(f"  Wave {wave_num}: {', '.join([name for name, _ in wave_agents])}")
        
        return agents
    
    @classmethod
    async def _create_agent(cls, agent_name: str, spec: Dict) -> tuple:
        """Create a single agent"""
        # Generate agent code
        agent_code = cls._generate_agent_code(agent_name, spec)
        
        # Write to file
        file_path = f"{agent_name}_agent.py"
        with open(file_path, 'w') as f:
            f.write(agent_code)
        
        print(f"  Created {agent_name}_agent.py")
        
        # Return agent name and spec for organization
        return (agent_name, spec)
    
    @classmethod
    def _generate_agent_code(cls, agent_name: str, spec: Dict) -> str:
        """Generate Python code for an agent"""
        class_name = ''.join(word.capitalize() for word in agent_name.split('_')) + 'Agent'
        
        code = f'''"""
{class_name} - {spec['description']}
Part of Licia's Research Lab V2
Wave {spec['wave']} Agent - Tier {spec['tier']} Security
"""

import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from base_agent import BaseAgent

class {class_name}(BaseAgent):
    """
    {spec['description']}
    
    Action Research Paradigm:
    - Documents what works in practice
    - Finds science to explain observed outcomes
    - Validates through systematic observation
    """
    
    def __init__(self):
        super().__init__("{agent_name}", permission_tier={spec['tier']})
        
        # Specialized vocabulary for {agent_name}
        self.vocabulary = {json.dumps(spec['vocabulary'], indent=12)}
        
        # Action research tracking
        self.practice_observations = []
        self.pattern_tracker = {{}}
        
    async def analyze(self, data: str, context: Dict = None) -> Dict[str, Any]:
        """
        Analyze transcript for {agent_name.replace('_', ' ')} patterns
        
        Action Research Approach:
        1. Document what happens in practice
        2. Identify emergent patterns
        3. Find scientific explanations
        """
        # Security validation first
        clean_data = self.validate_input(data)
        
        # Initialize results
        results = {{
            'agent': self.agent_type,
            'timestamp': datetime.now().isoformat(),
            'methodology': 'action_research',
            'findings': [],
            'patterns': [],
            'confidence': 0.0
        }}
        
        # Perform specialized analysis
        findings = self._analyze_{agent_name}(clean_data, context)
        results['findings'] = findings
        
        # Track patterns for action research
        self._track_patterns(findings)
        results['patterns'] = self._identify_patterns()
        
        # Calculate confidence
        results['confidence'] = self._calculate_confidence(findings)
        
        # Save to memory
        self.save_to_memory(results, {{
            'data_length': len(clean_data),
            'context': context or {{}},
            'wave': {spec['wave']}
        }})
        
        # Sign output
        results['signature'] = self.sign_output(results)
        
        return results
    
    def _analyze_{agent_name}(self, data: str, context: Dict = None) -> List[Dict]:
        """Specialized analysis for {agent_name.replace('_', ' ')}"""
        findings = []
        lines = data.split('\\n')
        
        # Search for vocabulary patterns
        for vocab_category, terms in self.vocabulary.items():
            for i, line in enumerate(lines):
                lower_line = line.lower()
                for term in terms:
                    if term.lower() in lower_line:
                        findings.append({{
                            'line_number': i + 1,
                            'category': vocab_category,
                            'term': term,
                            'context': line.strip(),
                            'confidence': self._assess_confidence(term, line)
                        }})
        
        return findings
    
    def _track_patterns(self, findings: List[Dict]):
        """Track patterns for action research methodology"""
        for finding in findings:
            pattern_key = f"{{finding['category']}}:{{finding['term']}}"
            if pattern_key not in self.pattern_tracker:
                self.pattern_tracker[pattern_key] = {{
                    'count': 0,
                    'contexts': [],
                    'first_seen': datetime.now().isoformat()
                }}
            
            self.pattern_tracker[pattern_key]['count'] += 1
            self.pattern_tracker[pattern_key]['contexts'].append(finding['context'])
    
    def _identify_patterns(self) -> List[Dict]:
        """Identify emergent patterns (inductive approach)"""
        patterns = []
        
        for pattern_key, data in self.pattern_tracker.items():
            if data['count'] >= 3:  # Pattern threshold
                patterns.append({{
                    'pattern': pattern_key,
                    'frequency': data['count'],
                    'strength': 'strong' if data['count'] >= 5 else 'moderate',
                    'action_research_note': 'Pattern emerged from practice observation'
                }})
        
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
'''
        
        return code

# Main execution
if __name__ == "__main__":
    async def main():
        print("🚀 Starting Agent Factory...")
        print("=" * 50)
        
        # Create all agents
        agents = await AgentFactory.create_all_agents()
        
        print("=" * 50)
        print(f"✅ Successfully created {len(agents)} agents")
        print("\nAgent files created in agents/ directory:")
        for agent_name in agents.keys():
            print(f"  - agents/{agent_name}_agent.py")
    
    # Run the factory
    asyncio.run(main())
