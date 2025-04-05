# utils/scoring_utils.py

from typing import Dict, Any, List, Tuple, Optional
import re
from collections import Counter

class ScoringUtils:
    """Utilities for scoring and evaluating responses"""

    @staticmethod
    def calculate_base_score(
        correct_count: int,
        total_count: int,
        weight: float = 1.0
    ) -> float:
        """Calculate base score with weight"""
        return (correct_count / total_count if total_count > 0 else 0) * weight

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        return ' '.join(text.lower().split())

    @staticmethod
    def find_keyword_matches(
        text: str,
        keywords: List[str]
    ) -> Tuple[List[str], float]:
        """Find matching keywords and calculate match ratio"""
        normalized_text = ScoringUtils.normalize_text(text)
        matches = [kw for kw in keywords if kw.lower() in normalized_text]
        ratio = len(matches) / len(keywords) if keywords else 0
        return matches, ratio

    @staticmethod
    def score_technical_response(
        response: str,
        criteria: List[str],
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Score technical response based on criteria and keywords
        Returns detailed scoring breakdown
        """
        result = {
            'score': 0.0,
            'matched_criteria': [],
            'matched_keywords': [],
            'completeness': 0.0,
            'technical_accuracy': 0.0,
            'suggestions': []
        }

        # Find criteria matches
        normalized_response = ScoringUtils.normalize_text(response)
        result['matched_criteria'] = [
            criterion for criterion in criteria
            if ScoringUtils.normalize_text(criterion) in normalized_response
        ]
        
        # Calculate completeness score based on criteria
        result['completeness'] = ScoringUtils.calculate_base_score(
            len(result['matched_criteria']),
            len(criteria),
            weight=0.6
        )

        # Find keyword matches
        result['matched_keywords'], keyword_ratio = ScoringUtils.find_keyword_matches(
            response, keywords
        )
        
        # Calculate technical accuracy from keyword usage
        result['technical_accuracy'] = keyword_ratio * 0.4

        # Calculate final score
        result['score'] = result['completeness'] + result['technical_accuracy']

        # Generate suggestions
        if result['completeness'] < 0.5:
            missing_criteria = set(criteria) - set(result['matched_criteria'])
            result['suggestions'].append(
                f"Consider addressing these points: {', '.join(missing_criteria)}"
            )
        
        if result['technical_accuracy'] < 0.5:
            unused_keywords = set(keywords) - set(result['matched_keywords'])
            result['suggestions'].append(
                f"Include key technical terms: {', '.join(unused_keywords)}"
            )

        return result

    @staticmethod
    def score_behavioral_response(
        response: str,
        expected_points: List[str],
        passion_indicators: List[str]
    ) -> Dict[str, Any]:
        """
        Score behavioral response looking for STAR method and passion indicators
        Returns detailed scoring breakdown
        """
        result = {
            'score': 0.0,
            'structure_score': 0.0,
            'content_score': 0.0,
            'passion_score': 0.0,
            'components_found': {
                'situation': False,
                'task': False,
                'action': False,
                'result': False
            },
            'matched_points': [],
            'passion_indicators_found': [],
            'feedback': []
        }

        # Check STAR components
        star_patterns = {
            'situation': r'\b(when|while|during|in)\b.*?\b(faced|encountered|had)\b',
            'task': r'\b(needed|required|had to|goal was)\b',
            'action': r'\b(implemented|developed|created|decided|took|made)\b',
            'result': r'\b(resulted in|achieved|accomplished|led to|improved)\b'
        }

        for component, pattern in star_patterns.items():
            result['components_found'][component] = bool(re.search(pattern, response, re.I))

        # Calculate structure score
        result['structure_score'] = ScoringUtils.calculate_base_score(
            sum(result['components_found'].values()),
            len(result['components_found']),
            weight=0.4
        )

        # Score content
        result['matched_points'], content_ratio = ScoringUtils.find_keyword_matches(
            response, expected_points
        )
        result['content_score'] = content_ratio * 0.4

        # Score passion
        result['passion_indicators_found'], passion_ratio = ScoringUtils.find_keyword_matches(
            response, passion_indicators
        )
        result['passion_score'] = passion_ratio * 0.2

        # Calculate final score
        result['score'] = (
            result['structure_score'] +
            result['content_score'] +
            result['passion_score']
        )

        # Generate feedback
        if result['structure_score'] < 0.3:
            missing_components = [
                comp for comp, found in result['components_found'].items()
                if not found
            ]
            result['feedback'].append(
                f"Structure needs improvement. Include {', '.join(missing_components)}"
            )

        if result['content_score'] < 0.3:
            result['feedback'].append(
                "Response could be more detailed and specific"
            )

        if result['passion_score'] < 0.15:
            result['feedback'].append(
                "Show more enthusiasm and personal investment in your response"
            )

        return result

    @staticmethod
    def score_system_design(
        response: str,
        required_components: List[str],
        best_practices: List[str],
        scalability_patterns: List[str]
    ) -> Dict[str, Any]:
        """
        Score system design response based on components and patterns
        Returns detailed scoring breakdown
        """
        result = {
            'score': 0.0,
            'components_score': 0.0,
            'best_practices_score': 0.0,
            'scalability_score': 0.0,
            'found_components': [],
            'used_practices': [],
            'scalability_patterns_found': [],
            'recommendations': []
        }

        # Score components
        result['found_components'], components_ratio = ScoringUtils.find_keyword_matches(
            response, required_components
        )
        result['components_score'] = components_ratio * 0.4

        # Score best practices
        result['used_practices'], practices_ratio = ScoringUtils.find_keyword_matches(
            response, best_practices
        )
        result['best_practices_score'] = practices_ratio * 0.3

        # Score scalability
        result['scalability_patterns_found'], scalability_ratio = ScoringUtils.find_keyword_matches(
            response, scalability_patterns
        )
        result['scalability_score'] = scalability_ratio * 0.3

        # Calculate final score
        result['score'] = (
            result['components_score'] +
            result['best_practices_score'] +
            result['scalability_score']
        )

        # Generate recommendations
        if result['components_score'] < 0.3:
            missing = set(required_components) - set(result['found_components'])
            result['recommendations'].append(
                f"Consider adding these components: {', '.join(missing)}"
            )

        if result['best_practices_score'] < 0.2:
            unused = set(best_practices) - set(result['used_practices'])
            result['recommendations'].append(
                f"Incorporate these best practices: {', '.join(unused)}"
            )

        if result['scalability_score'] < 0.2:
            missing_patterns = set(scalability_patterns) - set(result['scalability_patterns_found'])
            result['recommendations'].append(
                f"Address these scalability concerns: {', '.join(missing_patterns)}"
            )

        return result