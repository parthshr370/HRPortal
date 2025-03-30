import json
from typing import Dict, Any
from config.openrouter_config import OpenRouterConfig
import re

class JobMatchingAgent:
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.openrouter = OpenRouterConfig()
        self.model_config = self.openrouter.get_model_config('reasoning')
        
        # Load the prompt template
        with open('prompts/job_matching_prompt.txt', 'r') as file:
            self.prompt_template = file.read()

    def fix_json_string(self, json_str: str) -> str:
        """Fix common JSON formatting issues"""
        # Remove any leading/trailing whitespace
        text = json_str.strip()
        
        # Remove code block markers
        if text.startswith('```'):
            text = re.sub(r'^```.*\n', '', text)
            text = re.sub(r'\n```$', '', text)
        
        # Fix truncated or incomplete JSON
        if not text.endswith('}'):
            text = text + '}'
        
        # Fix missing quotes around property names
        text = re.sub(r'([{,]\s*)(\w+)(:)', r'\1"\2"\3', text)
        
        # Fix single quotes to double quotes
        text = text.replace("'", '"')
        
        # Fix missing commas between array elements
        text = re.sub(r'"\s*\n\s*"', '",\n"', text)
        
        # Fix trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        return text

    def clean_json_response(self, response_text: str) -> str:
        """Clean and validate JSON response"""
        print("\nOriginal response text:")
        print(response_text[:1000] + "..." if len(response_text) > 1000 else response_text)
        
        try:
            # First attempt: Basic cleaning
            cleaned_text = self.fix_json_string(response_text)
            print("\nCleaned text (first attempt):")
            print(cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text)
            
            # Try to parse it
            try:
                json.loads(cleaned_text)
                return cleaned_text
            except json.JSONDecodeError as e:
                print(f"\nFirst cleaning attempt failed: {str(e)}")
            
            # Second attempt: More aggressive cleaning
            # Remove all whitespace between values
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            # Ensure proper JSON structure
            cleaned_text = re.sub(r'{(\s+)?}', '{}', cleaned_text)
            cleaned_text = re.sub(r'\[(\s+)?\]', '[]', cleaned_text)
            
            # Fix unterminated strings
            if "Unterminated string" in str(e):
                match = re.search(r'line (\d+) column (\d+)', str(e))
                if match:
                    line_no, col_no = int(match.group(1)), int(match.group(2))
                    lines = cleaned_text.split('\n')
                    if 0 < line_no <= len(lines):
                        problem_line = lines[line_no - 1]
                        if col_no < len(problem_line):
                            # Add closing quote
                            lines[line_no - 1] = problem_line[:col_no] + '"' + problem_line[col_no:]
                            cleaned_text = '\n'.join(lines)
            
            print("\nCleaned text (second attempt):")
            print(cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text)
            
            # Validate JSON
            try:
                json.loads(cleaned_text)
                return cleaned_text
            except json.JSONDecodeError:
                # Third attempt: Extract just the JSON portion
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
                if json_match:
                    potential_json = json_match.group(0)
                    cleaned_json = self.fix_json_string(potential_json)
                    
                    # Add more aggressive fixes for common issues
                    # Fix unescaped quotes in strings
                    cleaned_json = re.sub(r'(?<=[^\\])"(?=[^,}\]:]*")', '\\"', cleaned_json)
                    
                    # Try to validate
                    try:
                        json.loads(cleaned_json)
                        return cleaned_json
                    except:
                        # Last resort - create a valid default structure
                        return json.dumps(self.create_default_analysis())
                else:
                    return json.dumps(self.create_default_analysis())
            
        except Exception as e:
            print(f"\nError in JSON cleaning: {str(e)}")
            # If all else fails, return a valid default structure
            return json.dumps(self.create_default_analysis())

    def create_default_analysis(self) -> Dict[str, Any]:
        """Create a default analysis structure if parsing fails"""
        return {
            "match_score": 0,
            "analysis": {
                "skills": {
                    "score": 0,
                    "matches": [],
                    "gaps": []
                },
                "experience": {
                    "score": 0,
                    "matches": [],
                    "gaps": []
                },
                "education": {
                    "score": 0,
                    "matches": [],
                    "gaps": []
                },
                "additional": {
                    "score": 0,
                    "matches": [],
                    "gaps": []
                }
            },
            "recommendation": "Unable to generate recommendation due to processing error",
            "key_strengths": [],
            "areas_for_consideration": ["Analysis failed - please try again"]
        }

    def match_job(self, candidate_profile: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Compare candidate profile against job description and return match analysis"""
        try:
            # Format the input content
            formatted_content = (
                f"Candidate Profile:\n{json.dumps(candidate_profile, indent=2)}\n\n"
                f"Job Description:\n{job_description}"
            )
            
            # Prepare messages for OpenRouter
            messages = self.openrouter.format_messages(
                system_prompt=self.prompt_template,
                user_content=formatted_content
            )
            
            # Make the API request
            response = self.openrouter.make_request(
                messages=messages,
                model=self.model_name,
                api_key=self.api_key,
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens']
            )
            
            # Get and clean the completion
            completion = self.openrouter.get_completion(response)
            cleaned_json = self.clean_json_response(completion)
            
            # Parse and validate the response with retry logic
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    match_analysis = json.loads(cleaned_json)
                    
                    if not self.validate_match_analysis(match_analysis):
                        print(f"\nValidation failed on attempt {attempt+1}, trying alternative approach...")
                        if attempt == max_attempts - 1:
                            print("\nAll validation attempts failed, using default analysis")
                            return self.create_default_analysis()
                        
                        # Try to fix the structure
                        match_analysis = self.fix_analysis_structure(match_analysis)
                        if self.validate_match_analysis(match_analysis):
                            return match_analysis
                    else:
                        return match_analysis
                
                except json.JSONDecodeError as e:
                    print(f"\nJSON decode error on attempt {attempt+1}: {str(e)}")
                    if attempt == max_attempts - 1:
                        return self.create_default_analysis()
                    
                    # Try more aggressive cleaning for next attempt
                    if "Unterminated string" in str(e):
                        match = re.search(r'line (\d+) column (\d+)', str(e))
                        if match:
                            line_no, col_no = int(match.group(1)), int(match.group(2))
                            lines = cleaned_json.split('\n')
                            if line_no <= len(lines):
                                problem_line = lines[line_no - 1]
                                lines[line_no - 1] = problem_line[:col_no] + '"' + problem_line[col_no:]
                                cleaned_json = '\n'.join(lines)
            
            # If we reach here, all attempts failed
            return self.create_default_analysis()
            
        except Exception as e:
            print(f"\nError in job matching: {str(e)}")
            return self.create_default_analysis()

    def fix_analysis_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Try to fix an invalid analysis structure"""
        default = self.create_default_analysis()
        
        # Start with the default and copy over valid parts
        try:
            # Copy match score if present and valid
            if "match_score" in analysis and isinstance(analysis["match_score"], (int, float)):
                default["match_score"] = analysis["match_score"]
            
            # Copy recommendation if present
            if "recommendation" in analysis and isinstance(analysis["recommendation"], str):
                default["recommendation"] = analysis["recommendation"]
            
            # Copy strengths and considerations if present
            if "key_strengths" in analysis and isinstance(analysis["key_strengths"], list):
                default["key_strengths"] = analysis["key_strengths"]
            
            if "areas_for_consideration" in analysis and isinstance(analysis["areas_for_consideration"], list):
                default["areas_for_consideration"] = analysis["areas_for_consideration"]
            
            # Try to salvage analysis sections
            if "analysis" in analysis and isinstance(analysis["analysis"], dict):
                for key in ["skills", "experience", "education", "additional"]:
                    if key in analysis["analysis"] and isinstance(analysis["analysis"][key], dict):
                        section = analysis["analysis"][key]
                        
                        # Create a valid section structure
                        valid_section = {
                            "score": 0,
                            "matches": [],
                            "gaps": []
                        }
                        
                        # Copy valid parts
                        if "score" in section and isinstance(section["score"], (int, float)):
                            valid_section["score"] = section["score"]
                        
                        if "matches" in section and isinstance(section["matches"], list):
                            valid_section["matches"] = section["matches"]
                        
                        if "gaps" in section and isinstance(section["gaps"], list):
                            valid_section["gaps"] = section["gaps"]
                        
                        default["analysis"][key] = valid_section
            
            return default
            
        except Exception:
            return default

    def validate_match_analysis(self, analysis: Dict[str, Any]) -> bool:
        """Validate the match analysis structure"""
        try:
            required_keys = ["match_score", "analysis", "recommendation", "key_strengths", "areas_for_consideration"]
            if not all(key in analysis for key in required_keys):
                return False

            analysis_keys = ["skills", "experience", "education", "additional"]
            if not all(key in analysis["analysis"] for key in analysis_keys):
                return False

            for key in analysis_keys:
                component = analysis["analysis"][key]
                if not all(k in component for k in ["score", "matches", "gaps"]):
                    return False
                if not isinstance(component["score"], (int, float)) or not 0 <= component["score"] <= 100:
                    return False

            return True
        except:
            return False