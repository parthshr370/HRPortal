# utils/md_parser.py

import re
from typing import Dict, Any, List, Optional
import frontmatter
import json

class MarkdownParser:
    """Utility for parsing structured markdown content"""
    
    @staticmethod
    def extract_sections(content: str) -> Dict[str, str]:
        """Extract main sections from markdown content"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            # Check for section headers
            header_match = re.match(r'^#+\s+(.+)$', line)
            if header_match:
                # Save previous section if exists
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                # Start new section
                current_section = header_match.group(1).lower()
                current_content = []
            else:
                # Add line to current section
                if current_section:
                    current_content.append(line)
                    
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections

    @staticmethod
    def parse_job_description(content: str) -> Dict[str, Any]:
        """Parse job description section"""
        parsed = {}
        
        # Extract basic info using regex
        title_match = re.search(r'(?:Title|Position):\s*(.+)', content)
        location_match = re.search(r'Location:\s*(.+)', content)
        experience_match = re.search(r'Experience.*?:\s*(.+)', content)
        
        if title_match:
            parsed['title'] = title_match.group(1).strip()
        if location_match:
            parsed['location'] = location_match.group(1).strip()
        if experience_match:
            parsed['experience_level'] = experience_match.group(1).strip()
            
        # Extract lists
        responsibilities = re.findall(r'(?:^|\n)[-•]\s*(.+)', content)
        qualifications = re.findall(r'(?:Requirements|Qualifications):\s*(?:\n[-•]\s*(.+))+', content)
        preferred = re.findall(r'(?:Preferred|Nice to have):\s*(?:\n[-•]\s*(.+))+', content)
        
        parsed['responsibilities'] = [r.strip() for r in responsibilities]
        parsed['qualifications'] = [q.strip() for q in qualifications]
        parsed['preferred_qualifications'] = [p.strip() for p in preferred] if preferred else []
        
        return parsed

    @staticmethod
    def parse_resume(content: str) -> Dict[str, Any]:
        """Parse resume section"""
        parsed = {
            'personal_info': {},
            'education': [],
            'experience': [],
            'skills': [],
            'projects': [],
            'certifications': []
        }
        
        # Extract personal info
        name_match = re.search(r'Name:\s*(.+)', content)
        email_match = re.search(r'Email:\s*(.+)', content)
        phone_match = re.search(r'Phone:\s*(.+)', content)
        
        if name_match:
            parsed['personal_info']['name'] = name_match.group(1).strip()
        if email_match:
            parsed['personal_info']['email'] = email_match.group(1).strip()
        if phone_match:
            parsed['personal_info']['phone'] = phone_match.group(1).strip()
            
        # Extract education
        education_section = re.search(r'Education:?\s*\n((?:.*\n)*?)(?:\n|$)', content)
        if education_section:
            education_entries = re.findall(
                r'[-•]?\s*(.+?)\s*(?:from|at)\s*(.+?)\s*\((.+?)\)',
                education_section.group(1)
            )
            for degree, institution, duration in education_entries:
                parsed['education'].append({
                    'degree': degree.strip(),
                    'institution': institution.strip(),
                    'duration': duration.strip()
                })
                
        # Extract experience
        experience_section = re.search(r'Experience:?\s*\n((?:.*\n)*?)(?:\n|$)', content)
        if experience_section:
            experience_blocks = re.split(r'\n(?=[-•])', experience_section.group(1))
            for block in experience_blocks:
                if not block.strip():
                    continue
                    
                title_match = re.search(r'[-•]?\s*(.+?)\s*(?:at|with)\s*(.+?)(?:\((.+?)\))?(?:\n|$)', block)
                if title_match:
                    experience = {
                        'title': title_match.group(1).strip(),
                        'company': title_match.group(2).strip(),
                        'duration': title_match.group(3).strip() if title_match.group(3) else None,
                        'responsibilities': []
                    }
                    
                    # Extract responsibilities
                    responsibilities = re.findall(r'[-•]\s*(.+?)(?:\n|$)', block)
                    experience['responsibilities'] = [r.strip() for r in responsibilities if r.strip()]
                    parsed['experience'].append(experience)
                    
        # Extract skills
        skills_section = re.search(r'Skills:?\s*\n((?:.*\n)*?)(?:\n|$)', content)
        if skills_section:
            skills = re.findall(r'[-•]?\s*([^,\n]+)(?:,|\n|$)', skills_section.group(1))
            parsed['skills'] = [s.strip() for s in skills if s.strip()]
            
        # Extract projects
        projects_section = re.search(r'Projects:?\s*\n((?:.*\n)*?)(?:\n|$)', content)
        if projects_section:
            project_blocks = re.split(r'\n(?=[-•])', projects_section.group(1))
            for block in project_blocks:
                if not block.strip():
                    continue
                    
                name_match = re.search(r'[-•]?\s*(.+?)(?:\n|$)', block)
                if name_match:
                    project = {
                        'name': name_match.group(1).strip(),
                        'description': [],
                        'technologies': []
                    }
                    
                    # Extract description points
                    descriptions = re.findall(r'[-•]\s*(.+?)(?:\n|$)', block)
                    project['description'] = [d.strip() for d in descriptions[1:] if d.strip()]
                    
                    # Extract technologies if mentioned
                    tech_match = re.search(r'Tech(?:nologies)?:\s*(.+?)(?:\n|$)', block)
                    if tech_match:
                        technologies = tech_match.group(1).split(',')
                        project['technologies'] = [t.strip() for t in technologies]
                        
                    parsed['projects'].append(project)
                    
        return parsed

    @staticmethod
    def parse_analysis(content: str) -> Dict[str, Any]:
        """Parse analysis section if present"""
        try:
            # Try to parse as JSON first
            return json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, try to extract structured information
            analysis = {
                'match_score': None,
                'strengths': [],
                'weaknesses': [],
                'recommendations': []
            }
            
            # Extract score if present
            score_match = re.search(r'(?:Score|Match):\s*(\d+)%?', content)
            if score_match:
                analysis['match_score'] = int(score_match.group(1))
                
            # Extract lists
            strengths = re.findall(r'Strengths?:?\s*(?:\n[-•]\s*(.+))+', content)
            weaknesses = re.findall(r'Weaknesses?:?\s*(?:\n[-•]\s*(.+))+', content)
            recommendations = re.findall(r'Recommendations?:?\s*(?:\n[-•]\s*(.+))+', content)
            
            analysis['strengths'] = [s.strip() for s in strengths]
            analysis['weaknesses'] = [w.strip() for w in weaknesses]
            analysis['recommendations'] = [r.strip() for r in recommendations]
            
            return analysis

    @classmethod
    def parse_full_content(cls, content: str) -> Dict[str, Any]:
        """Parse complete markdown content"""
        try:
            # Try to parse frontmatter if present
            post = frontmatter.loads(content)
            metadata = post.metadata
            content = post.content
        except:
            metadata = {}
            
        # Extract main sections
        sections = cls.extract_sections(content)
        
        # Parse each section
        parsed = {
            'metadata': metadata,
            'job_description': cls.parse_job_description(sections.get('job description', '')),
            'resume': cls.parse_resume(sections.get('resume', '')),
            'analysis': cls.parse_analysis(sections.get('analysis', '')) if 'analysis' in sections else None
        }
        
        return parsed