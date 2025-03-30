from typing import Dict, Any, Optional
import requests
import json
from .config import OPENROUTER_API_BASE, OPENROUTER_HEADERS, MODELS

class OpenRouterConfig:
    @staticmethod
    def get_headers(api_key: str) -> Dict[str, str]:
        """Get headers for OpenRouter API request"""
        headers = OPENROUTER_HEADERS.copy()
        headers["Authorization"] = f"Bearer {api_key}"
        return headers

    @staticmethod
    def make_request(
        messages: list,
        model: str,
        api_key: str,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Make a request to OpenRouter API"""
        headers = OpenRouterConfig.get_headers(api_key)
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            print("\nSending request to OpenRouter with data:")
            print(json.dumps(data, indent=2))
            
            response = requests.post(
                OPENROUTER_API_BASE,
                headers=headers,
                json=data,
                timeout=30  # 30 second timeout
            )
            
            response.raise_for_status()  # Raise exception for non-200 status codes
            
            response_data = response.json()
            print("\nReceived response from OpenRouter:")
            print(json.dumps(response_data, indent=2))
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API request failed: {str(e)}")

    @staticmethod
    def format_messages(system_prompt: str, user_content: str) -> list:
        """Format messages for OpenRouter API"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    @staticmethod
    def get_completion(response: Dict[str, Any]) -> Optional[str]:
        """Extract completion from OpenRouter response"""
        try:
            # Check if response has the expected structure
            if not isinstance(response, dict):
                raise ValueError("Response is not a dictionary")
                
            print("\nParsing OpenRouter response structure...")
            
            # Handle different response formats
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                elif 'text' in choice:
                    return choice['text']
            
            # If we reach here, the response format wasn't recognized
            print("\nUnexpected response format:")
            print(json.dumps(response, indent=2))
            raise ValueError(f"Unexpected response format: {response}")
            
        except Exception as e:
            raise Exception(f"Error extracting completion from response: {str(e)}")

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate OpenRouter API key"""
        try:
            headers = OpenRouterConfig.get_headers(api_key)
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def get_model_config(model_type: str) -> Dict[str, Any]:
        """Get model configuration"""
        if model_type not in MODELS:
            raise ValueError(f"Invalid model type: {model_type}")
        return MODELS[model_type]