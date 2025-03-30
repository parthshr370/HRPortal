# utils/llm_utils.py
import logging
import os
from typing import Dict, Any, Optional, List, Union
import requests
import json

# Import LangChain components
try:
    from langchain_community.chat_models import ChatOpenAI, ChatVertexAI, ChatAnthropic
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
    from langchain.schema import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger("llm_utils")

class LLMService:
    """Utility service for interacting with LLMs."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """Initialize the LLM service with configuration."""
        self.llm_config = llm_config
        self.provider = llm_config.get("provider", "mock")
        self.api_key = llm_config.get("api_key", "")
        self.model_name = llm_config.get("model_name", "gemini-pro")
        self.is_reasoning = llm_config.get("is_reasoning", True)
        
        # OpenRouter configurations
        self.openrouter_reason_key = os.environ.get("OPENROUTER_REASONING_API_KEY", "")
        self.openrouter_nonreason_key = os.environ.get("OPENROUTER_NON_REASONING_API_KEY", "")
        
        # Check for API keys and log status
        if self.provider == "openrouter":
            if self.is_reasoning and not self.openrouter_reason_key:
                logger.warning("OpenRouter REASONING API key not found in environment variables")
            elif not self.is_reasoning and not self.openrouter_nonreason_key:
                logger.warning("OpenRouter NON-REASONING API key not found in environment variables")
        
        # Check if LangChain is available
        if not LANGCHAIN_AVAILABLE and self.provider != "mock" and self.provider != "openrouter":
            logger.warning("LangChain not available. Using mock LLM.")
            self.provider = "mock"
        
        logger.info(f"Initialized LLM service with provider: {self.provider}, model: {self.model_name}")
        
        if self.provider == "openrouter":
            api_key_type = "reasoning" if self.is_reasoning else "non-reasoning"
            api_key_present = "YES" if (self.is_reasoning and self.openrouter_reason_key) or (not self.is_reasoning and self.openrouter_nonreason_key) else "NO"
            logger.info(f"OpenRouter {api_key_type} API key present: {api_key_present}")
        
        # Initialize LLM based on provider
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on the provider."""
        if self.provider == "mock":
            return None
        
        if self.provider == "openrouter":
            # For OpenRouter, we don't need to initialize a LangChain LLM
            # We'll directly use the requests API
            return None
        
        if not LANGCHAIN_AVAILABLE:
            logger.error("LangChain is required for non-mock LLM providers.")
            return None
        
        try:
            if self.provider == "openai":
                # Set up OpenAI API key
                os.environ["OPENAI_API_KEY"] = self.api_key
                
                return ChatOpenAI(
                    model_name=self.model_name,
                    temperature=0.2,
                    request_timeout=90
                )
            
            elif self.provider == "google" or self.provider == "gemini":
                # Set up Google API key
                os.environ["GOOGLE_API_KEY"] = self.api_key
                
                # For simplicity, using ChatOpenAI here
                # In a real implementation, we would use the appropriate Google client
                return ChatOpenAI(
                    model_name=self.model_name,
                    temperature=0.2,
                    request_timeout=90
                )
            
            elif self.provider == "anthropic":
                # Set up Anthropic API key
                os.environ["ANTHROPIC_API_KEY"] = self.api_key
                
                return ChatAnthropic(
                    model_name=self.model_name,
                    temperature=0.2,
                    request_timeout=90
                )
            
            else:
                logger.error(f"Unsupported LLM provider: {self.provider}")
                return None
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            return None
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, 
                      temperature: Optional[float] = None) -> Optional[str]:
        """Generate text from a prompt."""
        logger.info(f"Generating text with prompt: {prompt[:50]}...")
        
        if self.provider == "mock":
            return self._mock_generate_text(prompt, system_prompt)
        
        if self.provider == "openrouter":
            return self._openrouter_generate_text(prompt, system_prompt, temperature)
        
        if self.llm is None:
            logger.error("LLM not initialized.")
            return None
        
        try:
            # Create messages
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.append(HumanMessage(content=prompt))
            
            # Set temperature if provided
            if temperature is not None:
                self.llm.temperature = temperature
            
            # Generate response
            response = self.llm.invoke(messages)
            
            logger.info(f"Generated text: {response.content[:50]}...")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return None
    
    def _openrouter_generate_text(self, prompt: str, system_prompt: Optional[str] = None,
                                 temperature: Optional[float] = None) -> Optional[str]:
        """Generate text using OpenRouter API."""
        logger.info(f"Generating text with OpenRouter API, model: {self.model_name}")
        
        # Determine which API key to use based on reasoning flag
        api_key = self.openrouter_reason_key if self.is_reasoning else self.openrouter_nonreason_key
        key_type = "reasoning" if self.is_reasoning else "non-reasoning"
        
        if not api_key:
            logger.error(f"OpenRouter {key_type} API key not provided")
            return None
        
        # Prepare messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare request data
        data = {
            "messages": messages,
            "model": self.model_name,
            "temperature": temperature if temperature is not None else 0.2,
            "max_tokens": 1000
        }
        
        # Set up headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Make API request
            logger.info(f"Sending request to OpenRouter API with {key_type} key")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=30  # Add a timeout
            )
            
            # Parse response
            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"Generated text from OpenRouter: {content[:50]}...")
                return content
            else:
                logger.error(f"OpenRouter API error: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating text with OpenRouter: {str(e)}")
            return None
    
    def _mock_generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate mock text for testing."""
        logger.info("Using mock LLM to generate text")
        
        # Simple keyword-based response generation
        if "analyze" in prompt.lower() or "profile" in prompt.lower():
            return """
            Based on the candidate's profile, I've identified the following key skills:
            
            Core Skills:
            - Python (0.9): Strong proficiency evidenced in projects and experience
            - Machine Learning (0.8): Demonstrated through research and projects
            - Data Analysis (0.8): Strong foundation shown in technical skills
            
            Domain Skills:
            - PyTorch (0.9): Used extensively in research projects
            - LangChain (0.7): Applied in multiple projects
            - Flask (0.6): Used in web development projects
            
            The candidate has a strong background in machine learning and data science,
            with particular strength in deep learning with PyTorch and agent-based systems
            with LangChain.
            """
        
        elif "generate question" in prompt.lower():
            return """
            Question: Explain how LangChain agents can be orchestrated in a multi-agent system.
            Discuss the key components and patterns for effective agent communication.
            
            This question tests the candidate's understanding of:
            1. LangChain agent architecture
            2. Multi-agent orchestration patterns
            3. Communication protocols between agents
            4. LangGraph implementation details
            
            Difficulty: Medium
            Type: Open-ended
            Skills tested: LangChain, LangGraph, agent systems, software architecture
            """
        
        elif "reference answer" in prompt.lower():
            return """
            A comprehensive answer should include:
            
            1. LangChain agent basics:
            - Agents as autonomous components that can observe, reason, and act
            - Tool-using capabilities of agents
            - Memory and state management
            
            2. Multi-agent orchestration:
            - Using LangGraph for agent workflow definition
            - Sequential vs. parallel agent execution
            - Event-driven communication patterns
            
            3. Communication protocols:
            - Message passing between agents
            - Shared memory structures
            - API-based communication
            
            4. Implementation considerations:
            - Error handling and recovery
            - Performance optimization
            - Testing and debugging multi-agent systems
            
            The answer should demonstrate practical knowledge of implementing these concepts
            and awareness of trade-offs in different architectural decisions.
            """
        
        elif "evaluate" in prompt.lower():
            return """
            Score: 78/100
            
            Feedback:
            The candidate demonstrated good understanding of LangChain agents and multi-agent systems.
            They correctly explained the core components of agents and how they interact.
            
            Strengths:
            - Excellent explanation of LangChain agent architecture
            - Good description of message passing between agents
            - Practical examples provided
            
            Areas for improvement:
            - Could have elaborated more on LangGraph implementation details
            - Limited discussion of error handling and recovery
            - No mention of performance considerations
            
            The response shows solid foundational knowledge but lacks some advanced implementation details.
            """
        
        else:
            return "I am a mock LLM response for testing purposes."