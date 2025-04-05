# templates/prompt_templates/answer_gen_prompts.py

from langchain.prompts import PromptTemplate

# Prompt for generating coding question answers
CODING_ANSWER_PROMPT = PromptTemplate(
    input_variables=["question", "options"],
    template="""
    Generate a detailed answer explanation for this coding question.
    
    Question: {question}
    Options: {options}
    
    Create a comprehensive response in JSON format:
    {
        "correct_answer": {
            "option_index": index_of_correct_answer,
            "explanation": "detailed_explanation_of_why_this_is_correct"
        },
        "key_concepts": [
            {
                "concept": "concept_name",
                "explanation": "why_its_relevant"
            }
        ],
        "common_mistakes": [
            {
                "mistake": "potential_mistake",
                "explanation": "why_its_wrong"
            }
        ],
        "time_complexity": {
            "best_case": "O(x)",
            "average_case": "O(y)",
            "worst_case": "O(z)",
            "explanation": "complexity_analysis"
        },
        "code_example": "example_implementation",
        "best_practices": [
            "practice1",
            "practice2"
        ],
        "additional_resources": [
            {
                "topic": "related_topic",
                "description": "why_its_helpful_to_learn"
            }
        ]
    }
    """
)

# Prompt for generating system design answers
SYSTEM_DESIGN_ANSWER_PROMPT = PromptTemplate(
    input_variables=["scenario", "requirements", "constraints"],
    template="""
    Generate a model answer for this system design question.
    
    Scenario: {scenario}
    Requirements: {requirements}
    Constraints: {constraints}
    
    Provide a comprehensive solution in JSON format:
    {
        "architecture_components": [
            {
                "component": "component_name",
                "purpose": "why_needed",
                "specifications": ["spec1", "spec2"]
            }
        ],
        "design_decisions": [
            {
                "decision": "what_was_chosen",
                "rationale": "why_chosen",
                "alternatives": ["alternative1", "alternative2"],
                "trade_offs": {
                    "pros": ["pro1", "pro2"],
                    "cons": ["con1", "con2"]
                }
            }
        ],
        "scalability_approach": {
            "strategies": ["strategy1", "strategy2"],
            "justification": "why_these_strategies"
        },
        "reliability_measures": [
            {
                "measure": "measure_name",
                "implementation": "how_to_implement"
            }
        ],
        "security_considerations": [
            {
                "aspect": "security_aspect",
                "solution": "how_to_address"
            }
        ],
        "monitoring_and_maintenance": {
            "metrics": ["metric1", "metric2"],
            "alerts": ["alert1", "alert2"],
            "maintenance_tasks": ["task1", "task2"]
        },
        "evaluation_criteria": [
            {
                "criterion": "what_to_evaluate",
                "expected_standard": "what_good_looks_like",
                "scoring_guide": "how_to_score"
            }
        ]
    }
    """
)

# Prompt for generating behavioral answer criteria
BEHAVIORAL_ANSWER_PROMPT = PromptTemplate(
    input_variables=["question", "context", "experience_level"],
    template="""
    Generate evaluation criteria for this behavioral question.
    
    Question: {question}
    Context: {context}
    Experience Level: {experience_level}
    
    Create evaluation framework in JSON format:
    {
        "star_components": {
            "situation": {
                "required_elements": ["element1", "element2"],
                "scoring_criteria": "how_to_score"
            },
            "task": {
                "required_elements": ["element1", "element2"],
                "scoring_criteria": "how_to_score"
            },
            "action": {
                "required_elements": ["element1", "element2"],
                "scoring_criteria": "how_to_score"
            },
            "result": {
                "required_elements": ["element1", "element2"],
                "scoring_criteria": "how_to_score"
            }
        },
        "key_competencies": [
            {
                "competency": "competency_name",
                "indicators": ["indicator1", "indicator2"],
                "evaluation_method": "how_to_assess"
            }
        ],
        "passion_indicators": [
            {
                "indicator": "what_to_look_for",
                "examples": ["example1", "example2"]
            }
        ],
        "response_quality_levels": {
            "excellent": {
                "characteristics": ["char1", "char2"],
                "example_snippets": ["example1", "example2"]
            },
            "good": {
                "characteristics": ["char1", "char2"],
                "example_snippets": ["example1", "example2"]
            },
            "average": {
                "characteristics": ["char1", "char2"],
                "example_snippets": ["example1", "example2"]
            },
            "below_average": {
                "characteristics": ["char1", "char2"],
                "example_snippets": ["example1", "example2"]
            }
        },
        "red_flags": [
            {
                "flag": "what_to_watch_for",
                "impact": "why_its_concerning"
            }
        ],
        "scoring_guidelines": {
            "technical_competency": {
                "weight": 0.3,
                "scoring_criteria": "how_to_score"
            },
            "communication_clarity": {
                "weight": 0.2,
                "scoring_criteria": "how_to_score"
            },
            "problem_solving": {
                "weight": 0.3,
                "scoring_criteria": "how_to_score"
            },
            "passion_and_culture_fit": {
                "weight": 0.2,
                "scoring_criteria": "how_to_score"
            }
        }
    }
    """
)

# Prompt for generating answer rubrics with examples
ANSWER_RUBRIC_PROMPT = PromptTemplate(
    input_variables=["question_type", "question", "skill_level"],
    template="""
    Create a detailed answer rubric with examples for this question.
    
    Question Type: {question_type}
    Question: {question}
    Skill Level: {skill_level}
    
    Generate a comprehensive rubric in JSON format:
    {
        "scoring_levels": {
            "expert_level": {
                "score_range": "90-100",
                "requirements": ["req1", "req2"],
                "example_answers": ["example1", "example2"]
            },
            "proficient_level": {
                "score_range": "75-89",
                "requirements": ["req1", "req2"],
                "example_answers": ["example1", "example2"]
            },
            "competent_level": {
                "score_range": "60-74",
                "requirements": ["req1", "req2"],
                "example_answers": ["example1", "example2"]
            },
            "developing_level": {
                "score_range": "below 60",
                "requirements": ["req1", "req2"],
                "example_answers": ["example1", "example2"]
            }
        },
        "evaluation_dimensions": {
            "technical_accuracy": {
                "weight": 0.4,
                "criteria": ["criterion1", "criterion2"]
            },
            "solution_approach": {
                "weight": 0.3,
                "criteria": ["criterion1", "criterion2"]
            },
            "communication": {
                "weight": 0.3,
                "criteria": ["criterion1", "criterion2"]
            }
        },
        "bonus_points": [
            {
                "criterion": "what_earns_bonus",
                "points": "how_many_points",
                "example": "example_answer"
            }
        ],
        "instant_disqualifiers": [
            {
                "issue": "what_fails_immediately",
                "rationale": "why_its_critical"
            }
        ],
        "feedback_templates": {
            "strong_answer": "template_for_high_scores",
            "good_answer": "template_for_good_scores",
            "needs_improvement": "template_for_low_scores"
        }
    }
    """
)

# Prompt for automated answer validation
ANSWER_VALIDATION_PROMPT = PromptTemplate(
    input_variables=["proposed_answer", "evaluation_criteria"],
    template="""
    Validate this proposed answer against the evaluation criteria.
    
    Proposed Answer: {proposed_answer}
    Evaluation Criteria: {evaluation_criteria}
    
    Provide validation results in JSON format:
    {
        "validity_score": percentage_valid,
        "accuracy_check": {
            "technical_accuracy": score_0_to_1,
            "conceptual_correctness": score_0_to_1,
            "completeness": score_0_to_1
        },
        "criteria_assessment": [
            {
                "criterion": "criterion_name",
                "met": true_or_false,
                "evidence": "why_met_or_not"
            }
        ],
        "potential_issues": [
            {
                "issue": "potential_problem",
                "severity": "high/medium/low",
                "suggestion": "how_to_fix"
            }
        ],
        "improvement_suggestions": {
            "technical": ["suggestion1", "suggestion2"],
            "clarity": ["suggestion1", "suggestion2"],
            "completeness": ["suggestion1", "suggestion2"]
        }
    }
    """
)