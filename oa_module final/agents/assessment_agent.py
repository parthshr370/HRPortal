# agents/assessment_agent.py

from typing import Dict, Any, List
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
from models.data_models import Assessment, AssessmentResult

class AssessmentAgent:
    """Agent for evaluating candidate responses and generating feedback"""
    
    def __init__(self, reasoning_api_key: str):
        """Initialize with OpenAI API key for reasoning tasks"""
        self.llm = ChatOpenAI(
            model="openai/o3-mini",
            temperature=0.1,
            openai_api_key=reasoning_api_key
        )
        
        # Initialize prompts and chains
        self._init_prompts()
        
    def _init_prompts(self):
        """Initialize evaluation prompts for different question types"""
        
        # Coding evaluation prompt
        self.coding_eval_prompt = PromptTemplate(
            input_variables=["question", "candidate_answer", "expected_answer"],
            template="""
            Evaluate the following coding question response:
            
            Question: {question}
            Candidate's Answer: {candidate_answer}
            Expected Answer: {expected_answer}
            
            Provide a structured evaluation in JSON format:
            {
                "score": <int: 0-100>,
                "feedback": <string: detailed feedback>,
                "technical_accuracy": <float: 0-1>,
                "understanding_level": <string: basic/intermediate/advanced>,
                "improvement_areas": [<strings: areas for improvement>]
            }
            """
        )
        
        # System design evaluation prompt
        self.design_eval_prompt = PromptTemplate(
            input_variables=["scenario", "candidate_solution", "evaluation_criteria"],
            template="""
            Evaluate the following system design solution:
            
            Scenario: {scenario}
            Candidate's Solution: {candidate_solution}
            Evaluation Criteria: {evaluation_criteria}
            
            Provide a structured evaluation in JSON format:
            {
                "score": <int: 0-100>,
                "feedback": <string: detailed feedback>,
                "architecture_quality": <float: 0-1>,
                "scalability_consideration": <float: 0-1>,
                "security_consideration": <float: 0-1>,
                "strengths": [<strings: strong points>],
                "weaknesses": [<strings: areas to improve>]
            }
            """
        )
        
        # Behavioral evaluation prompt
        self.behavioral_eval_prompt = PromptTemplate(
            input_variables=["question", "response", "criteria", "passion_indicators"],
            template="""
            Evaluate the following behavioral response:
            
            Question: {question}
            Response: {response}
            Evaluation Criteria: {criteria}
            Passion Indicators to Look For: {passion_indicators}
            
            Provide a structured evaluation in JSON format:
            {
                "score": <int: 0-100>,
                "feedback": <string: detailed feedback>,
                "competency_rating": <float: 0-1>,
                "passion_rating": <float: 0-1>,
                "communication_clarity": <float: 0-1>,
                "key_strengths": [<strings: demonstrated strengths>],
                "development_areas": [<strings: areas for growth>]
            }
            """
        )

    async def evaluate_answer(
        self,
        question_type: str,
        question_data: Dict[str, Any],
        candidate_answer: str
    ) -> Dict[str, Any]:
        """Evaluate a single answer based on question type"""
        
        try:
            if question_type == "coding":
                result = await (self.coding_eval_prompt | self.llm).ainvoke(
                    question=question_data["text"],
                    candidate_answer=candidate_answer,
                    expected_answer=question_data["correct_answer"]
                )
                
            elif question_type == "system_design":
                result = await (self.design_eval_prompt | self.llm).ainvoke(
                    scenario=question_data["scenario"],
                    candidate_solution=candidate_answer,
                    evaluation_criteria=json.dumps(question_data["evaluation_criteria"])
                )
                
            elif question_type == "behavioral":
                result = await (self.behavioral_eval_prompt | self.llm).ainvoke(
                    question=question_data["text"],
                    response=candidate_answer,
                    criteria=json.dumps(question_data["evaluation_points"]),
                    passion_indicators=json.dumps(question_data["passion_indicators"])
                )
            else:
                raise ValueError(f"Unsupported question type: {question_type}")

            return json.loads(result.content)
            
        except Exception as e:
            print(f"Error evaluating {question_type} answer: {str(e)}")
            return {
                "score": 0,
                "feedback": f"Error evaluating answer: {str(e)}",
                "technical_accuracy": 0.0,
                "understanding_level": "error"
            }

    async def evaluate_assessment(
        self,
        assessment: Assessment,
        candidate_answers: Dict[str, str]
    ) -> AssessmentResult:
        """Evaluate complete assessment and generate final result"""
        
        question_scores = {}
        feedback = {}
        technical_ratings = []
        passion_ratings = []
        
        # Evaluate all question types
        for question_type, questions in [
            ("coding", assessment.coding_questions),
            ("system_design", assessment.system_design_questions),
            ("behavioral", assessment.behavioral_questions)
        ]:
            for question in questions:
                if question.id in candidate_answers:
                    result = await self.evaluate_answer(
                        question_type,
                        question.__dict__,
                        candidate_answers[question.id]
                    )
                    
                    question_scores[question.id] = result["score"]
                    feedback[question.id] = result["feedback"]
                    
                    # Collect ratings based on question type
                    if question_type == "coding":
                        technical_ratings.append(result["technical_accuracy"])
                    elif question_type == "system_design":
                        technical_ratings.append(result["architecture_quality"])
                        technical_ratings.append(result["scalability_consideration"])
                    elif question_type == "behavioral":
                        technical_ratings.append(result["competency_rating"])
                        passion_ratings.append(result["passion_rating"])

        # Calculate final scores and ratings
        total_score = sum(question_scores.values())
        passed = total_score >= assessment.passing_score
        
        avg_technical = sum(technical_ratings) / len(technical_ratings) if technical_ratings else 0.0
        avg_passion = sum(passion_ratings) / len(passion_ratings) if passion_ratings else 0.0

        return AssessmentResult(
            assessment_id=assessment.id,
            candidate_name=assessment.candidate_name,
            score=total_score,
            passed=passed,
            question_scores=question_scores,
            feedback=feedback,
            technical_rating=avg_technical,
            passion_rating=avg_passion
        )

    def generate_summary_report(self, result: AssessmentResult) -> str:
        """Generate a human-readable summary report"""
        
        report_template = """
        Assessment Summary for {candidate_name}
        =======================================
        
        Overall Results:
        - Total Score: {score}/100
        - Status: {status}
        - Technical Rating: {technical_rating:.2f}/1.0
        - Passion Rating: {passion_rating:.2f}/1.0
        
        Detailed Feedback:
        {detailed_feedback}
        
        Recommendations:
        {recommendations}
        """
        
        # Generate detailed feedback section
        detailed_feedback = "\n".join([
            f"- Question {qid}:\n  Score: {score}/100\n  {feedback}"
            for qid, (score, feedback) in zip(
                result.question_scores.keys(),
                zip(result.question_scores.values(), result.feedback.values())
            )
        ])
        
        # Generate recommendations based on scores
        recommendations = []
        if result.technical_rating < 0.7:
            recommendations.append("- Focus on strengthening technical fundamentals")
        if result.passion_rating < 0.7:
            recommendations.append("- Demonstrate more enthusiasm and interest in the role")
        if result.passed:
            recommendations.append("- Consider proceeding to next interview stage")
        else:
            recommendations.append("- Recommend additional preparation before proceeding")
            
        return report_template.format(
            candidate_name=result.candidate_name,
            score=result.score,
            status="PASSED" if result.passed else "FAILED",
            technical_rating=result.technical_rating,
            passion_rating=result.passion_rating,
            detailed_feedback=detailed_feedback,
            recommendations="\n".join(recommendations)
        )