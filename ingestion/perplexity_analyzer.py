"""
Perplexity Thread Analyzer for Licia's Research Lab V2
Analyzes 20+ Perplexity research threads with source ranking
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urlparse

class PerplexityAnalyzer:
    """Analyze Perplexity research threads with quality-based source ranking"""
    
    # Academic domains (Tier 1)
    ACADEMIC_DOMAINS = [
        '.edu', 'pubmed.ncbi', 'scholar.google', 'arxiv.org', 
        'doi.org', 'jstor.org', 'sciencedirect.com', 'nature.com',
        'science.org', 'pnas.org', 'cell.com', 'nejm.org',
        'thelancet.com', 'bmj.com', 'apa.org', 'sage.pub'
    ]
    
    # Professional domains (Tier 2)
    PROFESSIONAL_DOMAINS = [
        '.org', '.gov', 'harvard.edu', 'stanford.edu', 'mit.edu',
        'yale.edu', 'oxford.ac.uk', 'cambridge.org', 'nih.gov',
        'who.int', 'cdc.gov', 'mayo.edu', 'clevelandclinic.org',
        'hopkinsmedicine.org', 'psychologytoday.com'
    ]
    
    # Keywords indicating high-quality sources
    QUALITY_INDICATORS = [
        'peer-reviewed', 'journal', 'research', 'study', 'clinical trial',
        'meta-analysis', 'systematic review', 'PhD', 'Dr.', 'Professor',
        'Institute', 'University', 'Department', 'Laboratory'
    ]
    
    def __init__(self):
        self.processed_count = 0
        self.total_sources = 0
        self.tier_distribution = {'tier_1': 0, 'tier_2': 0, 'tier_3': 0}
        
    def analyze_threads(self, thread_files: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple Perplexity threads
        
        Args:
            thread_files: List of paths to Perplexity thread files (HTML or JSON)
            
        Returns:
            Comprehensive analysis with source ranking
        """
        synthesis = {
            'tier_1_academic': [],
            'tier_2_professional': [],
            'tier_3_general': [],
            'questions': [],
            'insights': [],
            'gaps': [],
            'themes': {},
            'quality_metrics': {},
            'metadata': {
                'total_threads': len(thread_files),
                'processed_at': datetime.now().isoformat()
            }
        }
        
        for thread_file in thread_files:
            try:
                # Process individual thread
                thread_analysis = self.analyze_single_thread(thread_file)
                
                # Aggregate sources by tier
                synthesis['tier_1_academic'].extend(thread_analysis['tier_1'])
                synthesis['tier_2_professional'].extend(thread_analysis['tier_2'])
                synthesis['tier_3_general'].extend(thread_analysis['tier_3'])
                
                # Collect questions and insights
                synthesis['questions'].extend(thread_analysis['questions'])
                synthesis['insights'].extend(thread_analysis['insights'])
                
                # Merge themes
                for theme, count in thread_analysis['themes'].items():
                    synthesis['themes'][theme] = synthesis['themes'].get(theme, 0) + count
                
                self.processed_count += 1
                
            except Exception as e:
                print(f"Error processing {thread_file}: {e}")
                synthesis['metadata']['errors'] = synthesis['metadata'].get('errors', [])
                synthesis['metadata']['errors'].append({
                    'file': thread_file,
                    'error': str(e)
                })
        
        # Calculate quality metrics
        synthesis['quality_metrics'] = self.calculate_quality_metrics(synthesis)
        
        # Identify gaps in research
        synthesis['gaps'] = self.identify_research_gaps(synthesis)
        
        # Create weighted synthesis
        synthesis['weighted_synthesis'] = self.create_weighted_synthesis(synthesis)
        
        return synthesis
    
    def analyze_single_thread(self, thread_file: str) -> Dict[str, Any]:
        """Analyze a single Perplexity thread"""
        
        # Determine file type and parse accordingly
        if thread_file.endswith('.html'):
            return self.parse_html_thread(thread_file)
        elif thread_file.endswith('.json'):
            return self.parse_json_thread(thread_file)
        else:
            # Try to parse as text
            return self.parse_text_thread(thread_file)
    
    def parse_html_thread(self, file_path: str) -> Dict[str, Any]:
        """Parse HTML format Perplexity thread"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract sources
        sources = self.extract_sources_from_html(soup)
        
        # Rank sources
        tier_1, tier_2, tier_3 = self.rank_sources(sources)
        
        # Extract questions
        questions = self.extract_questions_from_html(soup)
        
        # Extract insights
        insights = self.extract_insights_from_html(soup)
        
        # Extract themes
        themes = self.extract_themes_from_content(html_content)
        
        return {
            'file': os.path.basename(file_path),
            'tier_1': tier_1,
            'tier_2': tier_2,
            'tier_3': tier_3,
            'questions': questions,
            'insights': insights,
            'themes': themes,
            'total_sources': len(sources)
        }
    
    def parse_json_thread(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON format Perplexity thread"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sources = []
        questions = []
        insights = []
        
        # Extract based on common JSON structures
        if 'sources' in data:
            sources = data['sources']
        elif 'references' in data:
            sources = data['references']
        
        if 'questions' in data:
            questions = data['questions']
        elif 'query' in data:
            questions = [data['query']]
        
        if 'answer' in data:
            insights = self.extract_insights_from_text(data['answer'])
        
        # Rank sources
        tier_1, tier_2, tier_3 = self.rank_sources(sources)
        
        # Extract themes from all text content
        all_text = json.dumps(data)
        themes = self.extract_themes_from_content(all_text)
        
        return {
            'file': os.path.basename(file_path),
            'tier_1': tier_1,
            'tier_2': tier_2,
            'tier_3': tier_3,
            'questions': questions,
            'insights': insights,
            'themes': themes,
            'total_sources': len(sources)
        }
    
    def parse_text_thread(self, file_path: str) -> Dict[str, Any]:
        """Parse text format thread"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        sources = [{'url': url} for url in urls]
        
        # Extract questions
        questions = [line.strip() for line in content.split('\n') if line.strip().endswith('?')]
        
        # Extract insights
        insights = self.extract_insights_from_text(content)
        
        # Rank sources
        tier_1, tier_2, tier_3 = self.rank_sources(sources)
        
        # Extract themes
        themes = self.extract_themes_from_content(content)
        
        return {
            'file': os.path.basename(file_path),
            'tier_1': tier_1,
            'tier_2': tier_2,
            'tier_3': tier_3,
            'questions': questions,
            'insights': insights,
            'themes': themes,
            'total_sources': len(sources)
        }
    
    def extract_sources_from_html(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract sources from HTML content"""
        sources = []
        
        # Look for common patterns in Perplexity HTML
        # Sources might be in various formats
        
        # Pattern 1: Links with source class
        for link in soup.find_all('a', class_=re.compile('source|reference|citation')):
            source = {
                'url': link.get('href', ''),
                'title': link.get_text().strip(),
                'type': 'link'
            }
            sources.append(source)
        
        # Pattern 2: Numbered references
        for ref in soup.find_all(class_=re.compile('reference-item|source-item')):
            source = {
                'url': '',
                'title': ref.get_text().strip(),
                'type': 'reference'
            }
            # Try to find URL within the reference
            link = ref.find('a')
            if link:
                source['url'] = link.get('href', '')
            sources.append(source)
        
        # Pattern 3: All external links
        if not sources:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    source = {
                        'url': href,
                        'title': link.get_text().strip() or href,
                        'type': 'general'
                    }
                    sources.append(source)
        
        return sources
    
    def rank_sources(self, sources: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Rank sources into three quality tiers"""
        tier_1 = []
        tier_2 = []
        tier_3 = []
        
        for source in sources:
            url = source.get('url', '')
            title = source.get('title', '')
            
            # Calculate quality score
            quality_score = self.calculate_source_quality(url, title)
            source['quality_score'] = quality_score
            
            # Assign to tier based on domain and quality
            if self.is_academic_source(url):
                tier_1.append(source)
                self.tier_distribution['tier_1'] += 1
            elif self.is_professional_source(url):
                tier_2.append(source)
                self.tier_distribution['tier_2'] += 1
            else:
                tier_3.append(source)
                self.tier_distribution['tier_3'] += 1
            
            self.total_sources += 1
        
        # Sort within each tier by quality score
        tier_1.sort(key=lambda x: x['quality_score'], reverse=True)
        tier_2.sort(key=lambda x: x['quality_score'], reverse=True)
        tier_3.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return tier_1, tier_2, tier_3
    
    def is_academic_source(self, url: str) -> bool:
        """Check if URL is from an academic source"""
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.ACADEMIC_DOMAINS)
    
    def is_professional_source(self, url: str) -> bool:
        """Check if URL is from a professional source"""
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.PROFESSIONAL_DOMAINS)
    
    def calculate_source_quality(self, url: str, title: str = '') -> float:
        """Calculate quality score for a source (0-10)"""
        score = 5.0  # Base score
        
        # Boost for academic domains
        if self.is_academic_source(url):
            score += 3.0
        elif self.is_professional_source(url):
            score += 1.5
        
        # Check for quality indicators in title
        title_lower = title.lower()
        for indicator in self.QUALITY_INDICATORS:
            if indicator.lower() in title_lower:
                score += 0.5
                if score >= 10:
                    break
        
        # Check for recent publication (if year is mentioned)
        current_year = datetime.now().year
        year_pattern = r'\b(20[1-2][0-9])\b'
        years = re.findall(year_pattern, title + ' ' + url)
        if years:
            most_recent = max(int(year) for year in years)
            if most_recent >= current_year - 2:
                score += 1.0  # Very recent
            elif most_recent >= current_year - 5:
                score += 0.5  # Recent
        
        return min(10.0, score)
    
    def extract_questions_from_html(self, soup: BeautifulSoup) -> List[str]:
        """Extract questions from HTML content"""
        questions = []
        
        # Look for question patterns
        for element in soup.find_all(text=True):
            text = element.strip()
            if text and text.endswith('?'):
                questions.append(text)
        
        return questions
    
    def extract_insights_from_html(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract insights from HTML content"""
        insights = []
        
        # Look for summary or conclusion sections
        for section in soup.find_all(['div', 'section', 'p']):
            text = section.get_text().strip()
            if any(keyword in text.lower() for keyword in ['conclusion', 'summary', 'key finding', 'important']):
                insights.append({
                    'insight': text[:500],  # Limit length
                    'type': 'conclusion'
                })
        
        return insights
    
    def extract_insights_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract insights from plain text"""
        insights = []
        
        # Patterns indicating insights
        patterns = [
            r'(?i)in conclusion[,:]?\s*(.+?)(?:\.|$)',
            r'(?i)the key (?:finding|insight|point) is\s*(.+?)(?:\.|$)',
            r'(?i)importantly[,:]?\s*(.+?)(?:\.|$)',
            r'(?i)this (?:shows|suggests|indicates) that\s*(.+?)(?:\.|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                insights.append({
                    'insight': match.strip()[:500],
                    'type': 'extracted'
                })
        
        return insights
    
    def extract_themes_from_content(self, content: str) -> Dict[str, int]:
        """Extract themes from content"""
        themes = {}
        
        # Therapeutic and research themes
        theme_keywords = {
            'trauma': ['trauma', 'ptsd', 'traumatic', 'stress disorder'],
            'neuroscience': ['brain', 'neural', 'neuroscience', 'neuroplasticity'],
            'therapy': ['therapy', 'therapeutic', 'treatment', 'intervention'],
            'somatic': ['somatic', 'body', 'embodied', 'sensation'],
            'psychedelic': ['psychedelic', 'psilocybin', 'mdma', 'ketamine'],
            'attachment': ['attachment', 'bonding', 'relationship'],
            'mindfulness': ['mindfulness', 'meditation', 'awareness', 'present'],
            'regulation': ['regulation', 'dysregulation', 'nervous system'],
            'integration': ['integration', 'processing', 'consolidation'],
            'research': ['study', 'research', 'clinical trial', 'evidence']
        }
        
        content_lower = content.lower()
        
        for theme, keywords in theme_keywords.items():
            count = sum(content_lower.count(keyword) for keyword in keywords)
            if count > 0:
                themes[theme] = count
        
        return themes
    
    def calculate_quality_metrics(self, synthesis: Dict) -> Dict[str, Any]:
        """Calculate quality metrics for the synthesis"""
        total_sources = (
            len(synthesis['tier_1_academic']) +
            len(synthesis['tier_2_professional']) +
            len(synthesis['tier_3_general'])
        )
        
        if total_sources == 0:
            return {'error': 'No sources found'}
        
        metrics = {
            'total_sources': total_sources,
            'tier_1_percentage': (len(synthesis['tier_1_academic']) / total_sources) * 100,
            'tier_2_percentage': (len(synthesis['tier_2_professional']) / total_sources) * 100,
            'tier_3_percentage': (len(synthesis['tier_3_general']) / total_sources) * 100,
            'academic_ratio': len(synthesis['tier_1_academic']) / total_sources,
            'quality_score': self.calculate_overall_quality_score(synthesis),
            'source_diversity': self.calculate_source_diversity(synthesis)
        }
        
        return metrics
    
    def calculate_overall_quality_score(self, synthesis: Dict) -> float:
        """Calculate overall quality score (0-10)"""
        tier_1_count = len(synthesis['tier_1_academic'])
        tier_2_count = len(synthesis['tier_2_professional'])
        tier_3_count = len(synthesis['tier_3_general'])
        
        total = tier_1_count + tier_2_count + tier_3_count
        if total == 0:
            return 0.0
        
        # Weighted average: Tier 1 = 10, Tier 2 = 6, Tier 3 = 3
        score = (tier_1_count * 10 + tier_2_count * 6 + tier_3_count * 3) / total
        
        return round(score, 2)
    
    def calculate_source_diversity(self, synthesis: Dict) -> Dict[str, int]:
        """Calculate diversity of sources"""
        domains = set()
        
        for tier in ['tier_1_academic', 'tier_2_professional', 'tier_3_general']:
            for source in synthesis[tier]:
                url = source.get('url', '')
                if url:
                    parsed = urlparse(url)
                    domains.add(parsed.netloc)
        
        return {
            'unique_domains': len(domains),
            'sources_per_domain': len(synthesis['tier_1_academic'] + 
                                    synthesis['tier_2_professional'] + 
                                    synthesis['tier_3_general']) / max(len(domains), 1)
        }
    
    def identify_research_gaps(self, synthesis: Dict) -> List[str]:
        """Identify gaps in research coverage"""
        gaps = []
        
        # Check theme coverage
        expected_themes = ['trauma', 'neuroscience', 'therapy', 'somatic', 'research']
        covered_themes = set(synthesis['themes'].keys())
        
        for theme in expected_themes:
            if theme not in covered_themes:
                gaps.append(f"Limited coverage of {theme}")
        
        # Check source quality
        metrics = synthesis.get('quality_metrics', {})
        if metrics.get('tier_1_percentage', 0) < 20:
            gaps.append("Insufficient academic sources (less than 20%)")
        
        # Check for question coverage
        if len(synthesis['questions']) < 10:
            gaps.append("Limited research questions identified")
        
        return gaps
    
    def create_weighted_synthesis(self, synthesis: Dict) -> Dict[str, Any]:
        """Create a synthesis weighted by source quality"""
        weighted = {
            'high_confidence_claims': [],
            'moderate_confidence_claims': [],
            'low_confidence_claims': [],
            'key_questions': synthesis['questions'][:10],  # Top 10 questions
            'primary_themes': dict(sorted(synthesis['themes'].items(), 
                                        key=lambda x: x[1], 
                                        reverse=True)[:5])
        }
        
        # Process insights based on source tier
        for source in synthesis['tier_1_academic']:
            if 'insight' in source:
                weighted['high_confidence_claims'].append(source['insight'])
        
        for source in synthesis['tier_2_professional']:
            if 'insight' in source:
                weighted['moderate_confidence_claims'].append(source['insight'])
        
        for source in synthesis['tier_3_general']:
            if 'insight' in source:
                weighted['low_confidence_claims'].append(source['insight'])
        
        return weighted


def main():
    """Main entry point for Perplexity analysis"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python perplexity_analyzer.py <thread1> [thread2] ...")
        sys.exit(1)
    
    thread_files = sys.argv[1:]
    analyzer = PerplexityAnalyzer()
    
    print(f"Analyzing {len(thread_files)} Perplexity threads...")
    results = analyzer.analyze_threads(thread_files)
    
    # Save results
    output_file = 'outputs/perplexity_analysis_results.json'
    os.makedirs('outputs', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAnalysis complete!")
    print(f"- Threads processed: {analyzer.processed_count}")
    print(f"- Total sources: {analyzer.total_sources}")
    print(f"- Tier 1 (Academic): {analyzer.tier_distribution['tier_1']}")
    print(f"- Tier 2 (Professional): {analyzer.tier_distribution['tier_2']}")
    print(f"- Tier 3 (General): {analyzer.tier_distribution['tier_3']}")
    
    metrics = results.get('quality_metrics', {})
    print(f"\nQuality Metrics:")
    print(f"- Overall quality score: {metrics.get('quality_score', 0):.2f}/10")
    print(f"- Academic source ratio: {metrics.get('academic_ratio', 0):.2%}")
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
