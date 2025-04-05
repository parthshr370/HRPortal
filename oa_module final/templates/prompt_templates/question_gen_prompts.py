# templates/prompt_templates/question_gen_prompts.py

from langchain.prompts import PromptTemplate

# Prompt for generating coding questions
CODING_QUESTION_PROMPT = PromptTemplate(
    input_variables=["skills", "level", "template"],
    template="""
    Generate a coding question based on the candidate's skills and experience level.
    
    Skills: {skills}
    Experience Level: {level}
    Template Structure: {template}
    
    Generate a question that:
    1. Tests relevant technical knowledge
    2. Is appropriate for the experience level
    3. Relates to the candidate's skills
    4. Includes clear evaluation criteria
    
    Return the question in JSON format:
    {
        "id": "unique_identifier",
        "type": "coding",
        "text": "question_text",
        "options": ["option1", "option2", "option3", "option4"],
        "correct_option": 0,
        "explanation": "detailed_explanation",
        "difficulty": "easy/medium/hard",
        "score": points_value,
        "evaluation_criteria": ["criterion1", "criterion2"]
    }
    """
)

# Prompt for generating system design questions
SYSTEM_DESIGN_PROMPT = PromptTemplate(
    input_variables=["experience", "level", "template"],
    template="""
    Generate a system design question based on the candidate's experience and level.
    
    Experience: {experience}
    Level: {level}
    Template Structure: {template}
    
    Create a question that:
    1. Tests architectural knowledge
    2. Evaluates scalability understanding
    3. Checks security awareness
    4. Assesses trade-off analysis
    
    Return the question in JSON format:
    {
        "id": "unique_identifier",
        "type": "system_design",
        "scenario": "detailed_problem_description",
        "requirements": ["req1", "req2"],
        "constraints": ["constraint1", "constraint2"],
        "expected_components": ["component1", "component2"],
        "evaluation_criteria": ["criterion1", "criterion2"],
        "difficulty": "easy/medium/hard",
        "score": points_value
    }
    """
)

# Prompt for generating behavioral questions
BEHAVIORAL_PROMPT = PromptTemplate(
    input_variables=["resume_data", "job_desc", "template"],
    template="""
    Generate a behavioral question based on the candidate's resume and job requirements.
    
    Resume Data: {resume_data}
    Job Description: {job_desc}
    Template Structure: {template}
    
    Create a question that:
    1. Relates to candidate's experience
    2. Aligns with job requirements
    3. Evaluates soft skills
    4. Reveals passion and cultural fit
    
    Return the question in JSON format:
    {
        "id": "unique_identifier",
        "type": "behavioral",
        "text": "question_text",
        "context": "background_context",
        "evaluation_points": ["point1", "point2"],
        "passion_indicators": ["indicator1", "indicator2"],
        "difficulty": "easy/medium/hard",
        "score": points_value
    }
    """
)

# Prompt for evaluating responses
EVALUATION_PROMPT = PromptTemplate(
    input_variables=["question", "response", "criteria", "level"],
    template="""
    Evaluate the candidate's response against the given criteria.
    
    Question: {question}
    Response: {response}
    Evaluation Criteria: {criteria}
    Experience Level: {level}
    
    Provide evaluation in JSON format:
    {
        "score": points_awarded,
        "feedback": "detailed_feedback",
        "strengths": ["strength1", "strength2"],
        "areas_for_improvement": ["area1", "area2"],
        "technical_accuracy": rating_0_to_1,
        "communication_clarity": rating_0_to_1,
        "passion_indicators": ["indicator1", "indicator2"]
    }
    """
)

# Prompt for generating answer rubrics
RUBRIC_PROMPT = PromptTemplate(
    input_variables=["question", "level"],
    template="""
    Create a detailed rubric for evaluating responses to this question.
    
    Question: {question}
    Experience Level: {level}
    
    Generate rubric in JSON format:
    {
        "excellent_response": {
            "description": "what_constitutes_full_marks",
            "key_points": ["point1", "point2"],
            "examples": ["example1", "example2"]
        },
        "good_response": {
            "description": "what_constitutes_good_marks",
            "key_points": ["point1", "point2"]
        },
        "average_response": {
            "description": "what_constitutes_average_marks",
            "key_points": ["point1", "point2"]
        },
        "below_average_response": {
            "description": "what_constitutes_low_marks",
            "key_points": ["point1", "point2"]
        },
        "scoring_guidelines": {
            "technical_accuracy": "scoring_criteria",
            "communication": "scoring_criteria",
            "problem_solving": "scoring_criteria"
        }
    }
    """
)

# Prompt for customizing questions
CUSTOMIZATION_PROMPT = PromptTemplate(
    input_variables=["base_question", "candidate_info", "job_requirements"],
    template="""
    Customize this question based on the candidate's background and job requirements.
    
    Base Question: {base_question}
    Candidate Info: {candidate_info}
    Job Requirements: {job_requirements}
    
    Modify the question to:
    1. Reference candidate's specific experience
    2. Align with job-specific technical requirements
    3. Match the appropriate difficulty level
    4. Include relevant context
    
    Return customized question in JSON format:
    {
        "original_question": "base_question",
        "customized_question": "modified_question",
        "customization_rationale": "explanation",
        "specific_evaluation_points": ["point1", "point2"]
    }
    """
)

# Prompt for passion detection
PASSION_DETECTION_PROMPT = PromptTemplate(
    input_variables=["response", "role_requirements"],
    template="""
    Analyze the response for indicators of genuine interest and passion.
    
    Response: {response}
    Role Requirements: {role_requirements}
    
    Look for:
    1. Enthusiasm in technical discussions
    2. Depth of knowledge
    3. Personal projects or contributions
    4. Continuous learning
    5. Industry awareness
    
    Return analysis in JSON format:
    {
        "passion_score": rating_0_to_1,
        "indicators_found": ["indicator1", "indicator2"],
        "authenticity_assessment": "detailed_analysis",
        "cultural_fit_indicators": ["indicator1", "indicator2"],
        "growth_potential": "assessment"
    }
    """
)