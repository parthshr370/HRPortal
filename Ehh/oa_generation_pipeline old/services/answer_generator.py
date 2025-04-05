# services/answer_generator.py
import logging
from typing import Dict, List, Any, Optional
from uuid import uuid4

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from models.question import Question, ReferenceAnswer, QuestionType
from config.config import LLM_CONFIG  # Default is reasoning configuration

logger = logging.getLogger("answer_generator")

class AnswerGeneratorService:
    """Service to generate reference answers for assessment questions."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the service with LLM configuration."""
        logger.info("Initializing Answer Generator Service")
        
        # Use reasoning configuration by default (better for answer generation)
        self.llm_config = llm_config if llm_config else LLM_CONFIG
        
        logger.info(f"Using {self.llm_config.get('provider')} for answer generation with model {self.llm_config.get('model_name')}")
        
        # Define prompt templates for different question types
        self.prompt_templates = {
            QuestionType.MULTIPLE_CHOICE: """
            Generate a reference answer for the following multiple choice question.
            Question: {question}
            
            Provide the correct option and an explanation for why this option is correct and why other options are incorrect.
            
            Your answer should include:
            1. The correct option
            2. A detailed explanation
            3. Key points that should be included in any correct answer
            """,
            
            QuestionType.CODING: """
            Generate a reference answer for the following coding question.
            Question: {question}
            
            Provide a complete, working solution with an explanation of how it works and why you approached it this way.
            
            Your answer should include:
            1. Complete code solution
            2. Explanation of the approach
            3. Time and space complexity analysis
            4. Key points that should be checked when evaluating a candidate's response
            """,
            
            QuestionType.SHORT_ANSWER: """
            Generate a reference answer for the following short answer question.
            Question: {question}
            
            Provide a concise but complete answer that covers all important aspects.
            
            Your answer should include:
            1. A direct answer to the question
            2. Key concepts that must be included
            3. Common misconceptions to watch for
            """,
            
            QuestionType.OPEN_ENDED: """
            Generate a reference answer for the following open-ended question.
            Question: {question}
            
            Provide a comprehensive answer that could serve as a model response.
            
            Your answer should include:
            1. A structured response covering all relevant aspects
            2. Key points that must be addressed
            3. Additional points that would enhance the answer
            4. A scoring rubric with weighted importance of different components
            """
        }
    
    def generate_reference_answers(self, questions: List[Question]) -> List[ReferenceAnswer]:
        """Generate reference answers for a list of questions."""
        logger.info(f"Generating reference answers for {len(questions)} questions")
        
        reference_answers = []
        for question in questions:
            try:
                answer = self._generate_reference_answer(question)
                if answer:
                    reference_answers.append(answer)
            except Exception as e:
                logger.error(f"Error generating reference answer for question {question.question_id}: {str(e)}")
        
        logger.info(f"Successfully generated {len(reference_answers)} reference answers")
        return reference_answers
    
    def _generate_reference_answer(self, question: Question) -> Optional[ReferenceAnswer]:
        """Generate a reference answer for a question."""
        logger.info(f"Generating reference answer for question {question.question_id}")
        
        # In a production environment, we would use the LLM to generate the answer
        # Here's how it would be structured:
        
        """
        # Get the appropriate prompt template
        prompt_template = self.prompt_templates.get(question.question_type)
        if not prompt_template:
            logger.error(f"No prompt template found for question type {question.question_type}")
            return None
        
        # Create prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["question"]
        )
        
        # Initialize LLM
        llm = ChatOpenAI(
            model_name=self.llm_config.get("model_name", "gpt-4"),
            temperature=0.2  # Lower temperature for more factual responses
        )
        
        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Generate answer
        result = chain.run(question=question.content)
        """
        
        # For now, we'll create mock answers based on question type
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            content = "The correct answer is option C. This is because..."
            key_points = ["Identifies option C as correct", "Explains why C is correct", "Explains why other options are incorrect"]
            scoring_rubric = {
                "Correct option identification": 0.3,
                "Explanation of correct option": 0.4,
                "Explanation of incorrect options": 0.3
            }
            explanation = "A complete answer must identify the correct option and provide reasoning."
        
        elif question.question_type == QuestionType.CODING:
            content = """
```python
def solve_problem(input_data):
    # Solution implementation
    result = []
    for item in input_data:
        # Process each item
        result.append(item * 2)
    return result

# Example usage
test_data = [1, 2, 3, 4, 5]
print(solve_problem(test_data))  # Output: [2, 4, 6, 8, 10]
```

This solution works by iterating through each item in the input and doubling it. 
The time complexity is O(n) where n is the length of the input list.
Space complexity is also O(n) for the result list.
"""
            key_points = [
                "Correct function definition", 
                "Proper iteration through input", 
                "Correct transformation of data",
                "Return appropriate result",
                "Time/space complexity analysis"
            ]
            scoring_rubric = {
                "Function correctness": 0.4,
                "Algorithm implementation": 0.3,
                "Code style and documentation": 0.1,
                "Complexity analysis": 0.2
            }
            explanation = "The solution must correctly process each item in the input and return the transformed data."
        
        elif question.question_type == QuestionType.SHORT_ANSWER:
            content = "The key concept is X which involves Y and Z principles. It's commonly applied in contexts A and B."
            key_points = ["Definition of X", "Relationship to Y and Z", "Application contexts"]
            scoring_rubric = {
                "Accurate definition": 0.4,
                "Identifying relationships": 0.3,
                "Practical applications": 0.3
            }
            explanation = "An answer should clearly define the concept and identify its relationships and applications."
        
        elif question.question_type == QuestionType.OPEN_ENDED:
            content = """
The solution to this problem involves several considerations:

1. First, we need to understand the underlying principles of A, B, and C.
2. Next, we must apply these principles to the specific context described.
3. We should consider the trade-offs between different approaches.
4. Finally, we must formulate a recommendation based on the analysis.

Approach 1 has advantages X and Y, but disadvantages Z.
Approach 2 addresses Z, but introduces new challenges P and Q.

The optimal solution likely combines elements of both approaches by...
"""
            key_points = [
                "Understanding of core principles",
                "Application to specific context",
                "Analysis of trade-offs",
                "Formulation of recommendations",
                "Justification of conclusions"
            ]
            scoring_rubric = {
                "Comprehensive understanding": 0.25,
                "Critical analysis": 0.25,
                "Solution development": 0.25,
                "Justification": 0.25
            }
            explanation = "A complete response should demonstrate understanding, analysis, solution development, and justification."
        
        else:
            logger.warning(f"Unsupported question type: {question.question_type}")
            return None
        
        # Create a reference answer
        reference_answer = ReferenceAnswer(
            answer_id=str(uuid4()),
            question_id=question.question_id,
            content=content,
            key_points=key_points,
            scoring_rubric=scoring_rubric,
            explanation=explanation
        )
        
        logger.info(f"Successfully generated reference answer {reference_answer.answer_id}")
        return reference_answer