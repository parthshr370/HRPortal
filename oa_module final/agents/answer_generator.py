# agents/answer_generator.py

from typing import Dict, Any, List
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json

class AnswerGenerator:
    """Agent for generating model answers and evaluation criteria"""
    
    def __init__(self, reasoning_api_key: str):
        self.llm = ChatOpenAI(
            model="openai/o3-mini",
            temperature=0.3,
            openai_api_key=reasoning_api_key
        )
        
        self._init_prompts()
        self._init_chains()
        
    def _init_prompts(self):
        """Initialize answer generation prompts"""
        self.coding_answer_prompt = PromptTemplate(
            input_variables=["question", "options"],
            template="""
            Generate a detailed explanation for this coding question:
            
            Question: {question}
            Options: {options}
            
            Provide the following in JSON format:
            {
                "correct_option": <int: index of correct option>,
                "explanation": <string: detailed explanation>,
                "key_concepts": [<string: important concepts>],
                "common_mistakes": [<string: typical errors>]
            }
            """
        )
        
        self.design_answer_prompt = PromptTemplate(
            input_variables=["scenario", "level"],
            template="""
            Create model answer criteria for this system design question:
            
            Scenario: {scenario}
            Level: {level}
            
            Provide the following in JSON format:
            {
                "expected_components": [<string: required components>],
                "evaluation_criteria": [<string: assessment points>],
                "architecture_patterns": [<string: relevant patterns>],
                "scalability_considerations": [<string: scaling aspects>],
                "security_considerations": [<string: security aspects>]
            }
            """
        )
        
        self.behavioral_answer_prompt = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            Generate evaluation criteria for this behavioral question:
            
            Question: {question}
            Context: {context}
            
            Provide the following in JSON format:
            {
                "evaluation_points": [<string: assessment criteria>],
                "passion_indicators": [<string: signs of genuine interest>],
                "communication_aspects": [<string: delivery points>],
                "red_flags": [<string: concerning responses>],
                "exemplar_answers": [<string: example good responses>]
            }
            """
        )
        
    def _init_chains(self):
        """Initialize LangChain chains"""
        self.coding_chain = LLMChain(llm=self.llm, prompt=self.coding_answer_prompt)
        self.design_chain = LLMChain(llm=self.llm, prompt=self.design_answer_prompt)
        self.behavioral_chain = LLMChain(llm=self.llm, prompt=self.behavioral_answer_prompt)
        
    async def generate_coding_answer(
        self,
        question: str,
        options: List[str]
    ) -> Dict[str, Any]:
        """Generate answer and explanation for coding question"""
        try:
            result = await self.coding_chain.arun(
                question=question,
                options=json.dumps(options)
            )
            return json.loads(result)
        except Exception as e:
            print(f"Error generating coding answer: {str(e)}")
            return {
                "correct_option": 0,
                "explanation": "Error generating answer",
                "key_concepts": [],
                "common_mistakes": []
            }
            
    async def generate_design_criteria(
        self,
        scenario: str,
        level: str
    ) -> Dict[str, Any]:
        """Generate evaluation criteria for system design question"""
        try:
            result = await self.design_chain.arun(
                scenario=scenario,
                level=level
            )
            return json.loads(result)
        except Exception as e:
            print(f"Error generating design criteria: {str(e)}")
            return {
                "expected_components": [],
                "evaluation_criteria": [],
                "architecture_patterns": [],
                "scalability_considerations": [],
                "security_considerations": []
            }
            
    async def generate_behavioral_criteria(
        self,
        question: str,
        context: str
    ) -> Dict[str, Any]:
        """Generate evaluation criteria for behavioral question"""
        try:
            result = await self.behavioral_chain.arun(
                question=question,
                context=context
            )
            return json.loads(result)
        except Exception as e:
            print(f"Error generating behavioral criteria: {str(e)}")
            return {
                "evaluation_points": [],
                "passion_indicators": [],
                "communication_aspects": [],
                "red_flags": [],
                "exemplar_answers": []
            }