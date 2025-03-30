import json
from typing import Dict, Any
from config.openrouter_config import OpenRouterConfig
import re

class DecisionFeedbackAgent:
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.openrouter = OpenRouterConfig()
        self.model_config = self.openrouter.get_model_config('reasoning')
        
        # Load the prompt template
        with open('prompts/decision_feedback_prompt.txt', 'r') as file:
            self.prompt_template = file.read()

    def clean_json_response(self, response_text: str) -> str:
        """Clean and fix common JSON formatting issues in API responses"""
        print("\nOriginal response text:")
        print(response_text[:1000] + "..." if len(response_text) > 1000 else response_text)
        
        # Remove markdown code blocks
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        
        # Try to extract just the JSON object
        json_pattern = r'({[\s\S]*})'
        match = re.search(json_pattern, cleaned_text)
        if match:
            cleaned_text = match.group(1)
        
        # First, check if it's already valid JSON
        try:
            json.loads(cleaned_text)
            print("\nJSON is already valid, no cleaning needed.")
            return cleaned_text
        except json.JSONDecodeError as e:
            print(f"\nJSON parsing error: {str(e)}. Attempting to fix...")
        
        # Apply multiple fixing strategies in sequence
        
        # 1. Fix common JSON issues
        # Add quotes to keys
        cleaned_text = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', cleaned_text)
        
        # Fix single quotes to double quotes
        cleaned_text = cleaned_text.replace("'", '"')
        
        # Fix missing commas
        cleaned_text = re.sub(r'"(\s*)\n(\s*)"', '",\n"', cleaned_text)
        
        # Fix trailing commas
        cleaned_text = re.sub(r',(\s*[}\]])', r'\1', cleaned_text)
        
        # 2. Try to parse after first round of fixes
        try:
            json.loads(cleaned_text)
            print("\nJSON fixed with basic cleaning.")
            return cleaned_text
        except json.JSONDecodeError as e:
            print(f"\nBasic cleaning failed: {str(e)}. Attempting more aggressive fixes...")
        
        # 3. Apply structural fixes
        
        # Handle unterminated strings
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
        
        # Handle missing commas
        if "Expecting ',' delimiter" in str(e):
            match = re.search(r'line (\d+) column (\d+)', str(e))
            if match:
                line_no, col_no = int(match.group(1)), int(match.group(2))
                lines = cleaned_text.split('\n')
                if 0 < line_no <= len(lines):
                    problem_line = lines[line_no - 1]
                    if col_no <= len(problem_line):
                        # Try to insert a comma at the problematic position
                        lines[line_no - 1] = problem_line[:col_no] + ',' + problem_line[col_no:]
                        cleaned_text = '\n'.join(lines)
        
        # 4. Try more aggressive structural parsing
        try:
            # Split into lines
            lines = cleaned_text.split('\n')
            fixed_lines = []
            in_key = False
            
            # Process line by line to fix structural issues
            for i, line in enumerate(lines):
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Process line content
                processed_line = line
                
                # Check if we're at a property line
                if ':' in line:
                    # Make sure key has quotes
                    key_part = line.split(':', 1)[0].strip()
                    if not (key_part.startswith('"') and key_part.endswith('"')):
                        processed_line = re.sub(r'(\s*)(\w+)(\s*:)', r'\1"\2"\3', line)
                
                # Check if this line should end with a comma
                if i < len(lines) - 1:
                    next_line = lines[i+1].strip()
                    # If next line starts a new property and this isn't the end of an object/array
                    if (':' in next_line or next_line.startswith('"')) and not (
                        processed_line.strip().endswith(',') or 
                        processed_line.strip().endswith('{') or 
                        processed_line.strip().endswith('[')
                    ):
                        # And this line isn't the end of an object/array
                        if not (processed_line.strip().endswith('}') or processed_line.strip().endswith(']')):
                            processed_line = processed_line.rstrip() + ','
                
                fixed_lines.append(processed_line)
            
            # Rejoin the fixed lines
            cleaned_text = '\n'.join(fixed_lines)
            
            # Try parsing again
            try:
                json.loads(cleaned_text)
                print("\nJSON fixed with structural parsing.")
                return cleaned_text
            except json.JSONDecodeError as e:
                print(f"\nStructural parsing failed: {str(e)}. Continuing with more fixes...")
            
        except Exception as parsing_error:
            print(f"\nError during structural parsing: {str(parsing_error)}")
        
        # Try the specific fix for the decision JSON (line 26 issue)
        try:
            fixed_json = self.fix_decision_delimiter_error(cleaned_text)
            json.loads(fixed_json)  # Test if it's valid
            print("\nJSON fixed with specific decision delimiter fix.")
            return fixed_json
        except:
            pass
        
        print("\nCleaned JSON:")
        print(cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text)
        return cleaned_text

    def fix_decision_delimiter_error(self, json_str: str) -> str:
        """Fix the specific delimiter error we're encountering in the decision JSON"""
        try:
            # Check if we can locate the error around line 26, column 32
            lines = json_str.split("\n")
            if len(lines) >= 26:
                # Get the problematic line (line 26)
                problem_line = lines[25]  # 0-indexed
                
                print(f"\nProblem line: {problem_line}")
                
                # Check if we can find a pattern that might need a comma
                if len(problem_line) >= 32:
                    # Insert a comma at position 32 or nearby
                    fixed_line = problem_line[:32] + ',' + problem_line[32:]
                    lines[25] = fixed_line
                    
                    # Rebuild the JSON
                    fixed_json = "\n".join(lines)
                    
                    # Try parsing it
                    try:
                        json.loads(fixed_json)
                        print("\nSuccessfully fixed the delimiter error")
                        return fixed_json
                    except json.JSONDecodeError as e:
                        print(f"\nOur specific fix didn't work: {str(e)}")
            
            # If we can't fix it with the line info, try a more general approach
            # Fix missing commas inside hiring_manager_notes section
            hiring_notes_pattern = r'("hiring_manager_notes"\s*:\s*{[^}]*})'
            match = re.search(hiring_notes_pattern, json_str)
            if match:
                hiring_notes_section = match.group(1)
                
                # Check for the common pattern where a comma is missing between properties
                fixed_section = re.sub(r'("\s*)\n(\s*")', r'\1,\n\2', hiring_notes_section)
                
                # Replace the original section with the fixed section
                fixed_json = json_str.replace(hiring_notes_section, fixed_section)
                
                try:
                    json.loads(fixed_json)
                    print("\nFixed delimiter issues in hiring_manager_notes section")
                    return fixed_json
                except:
                    pass
            
            return json_str
        except Exception as e:
            print(f"\nError in fix_decision_delimiter_error: {str(e)}")
            return json_str

    def fix_json_at_error(self, json_str: str, error_msg: str) -> str:
        """Attempt to fix JSON at the specific error location"""
        try:
            # Handle unterminated string errors
            if "Unterminated string" in error_msg:
                # Extract line and column from error message
                match = re.search(r'line (\d+) column (\d+)', error_msg)
                if match:
                    line_no, col_no = int(match.group(1)), int(match.group(2))
                    lines = json_str.split('\n')
                    if line_no <= len(lines):
                        problem_line = lines[line_no - 1]
                        # Add a closing quote
                        lines[line_no - 1] = problem_line[:col_no] + '"' + problem_line[col_no:]
                        return '\n'.join(lines)
            
            # Handle missing comma errors
            if "Expecting ',' delimiter" in error_msg or "delimiter" in error_msg:
                match = re.search(r'line (\d+) column (\d+)', error_msg)
                if match:
                    line_no, col_no = int(match.group(1)), int(match.group(2))
                    lines = json_str.split('\n')
                    if 0 < line_no <= len(lines):
                        problem_line = lines[line_no - 1]
                        
                        # Try to insert a comma at the problematic position
                        if col_no <= len(problem_line):
                            # Find where we need to add the comma - typically after a value and before the next key
                            # Look for patterns like "value"[space]"key" and insert comma between them
                            fixed_line = ""
                            if col_no < len(problem_line):
                                # Insert comma at the problematic position
                                fixed_line = problem_line[:col_no] + ',' + problem_line[col_no:]
                            else:
                                # Append comma at the end
                                fixed_line = problem_line + ','
                            
                            lines[line_no - 1] = fixed_line
                            fixed_json = '\n'.join(lines)
                            
                            # Verify the fix worked
                            try:
                                json.loads(fixed_json)
                                return fixed_json
                            except:
                                # If it didn't work, try a more aggressive approach
                                pass
            
            # Try more aggressive fixes for specific patterns
            
            # Fix missing commas between array elements or object properties
            json_str = re.sub(r'"\s*}\s*{', '"},{"', json_str)
            json_str = re.sub(r'"\s*]\s*\[', '"],["', json_str)
            
            # Fix common pattern where comma is missing between a value and the next property
            json_str = re.sub(r'"\s*"', '","', json_str)
            json_str = re.sub(r'"(\s*)}', '"}', json_str)
            json_str = re.sub(r'"(\s*)]', '"]', json_str)
            
            # Fix commas before closing brackets
            json_str = re.sub(r',(\s*})$', '}', json_str)
            json_str = re.sub(r',(\s*])$', ']', json_str)
            
            # If all else fails, return the original
            return json_str
        except:
            return json_str

    def create_default_decision(self) -> Dict[str, Any]:
        """Create a default decision structure if parsing fails"""
        return {
            "decision": {
                "status": "HOLD",
                "confidence_score": 50,
                "interview_stage": "SCREENING"
            },
            "rationale": {
                "key_strengths": ["Unable to determine due to processing error"],
                "concerns": ["Unable to process candidate data completely"],
                "risk_factors": ["Decision based on incomplete information"]
            },
            "recommendations": {
                "interview_focus": ["Verify resume contents manually"],
                "skill_verification": ["Conduct thorough technical assessment"],
                "discussion_points": ["Discuss areas mentioned in resume"]
            },
            "hiring_manager_notes": {
                "salary_band_fit": "Unable to determine",
                "growth_trajectory": "Unable to determine",
                "team_fit_considerations": "Manual assessment required",
                "onboarding_requirements": ["Standard onboarding process"]
            },
            "next_steps": {
                "immediate_actions": ["Re-run analysis or manually review"],
                "required_approvals": ["Hiring manager approval needed"],
                "timeline_recommendation": "Proceed with caution due to data processing issues"
            }
        }

    def generate_decision(
        self,
        candidate_profile: Dict[str, Any],
        match_analysis: Dict[str, Any],
        job_requirements: str
    ) -> Dict[str, Any]:
        """Generate a comprehensive hiring decision"""
        try:
            # Format input data
            formatted_content = (
                f"Candidate Profile:\n{json.dumps(candidate_profile, indent=2)}\n\n"
                f"Match Analysis:\n{json.dumps(match_analysis, indent=2)}\n\n"
                f"Job Requirements:\n{job_requirements}"
            )
            
            # Format messages for OpenRouter
            messages = self.openrouter.format_messages(
                system_prompt=self.prompt_template,
                user_content=formatted_content
            )
            
            try:
                # Make request to OpenRouter
                response = self.openrouter.make_request(
                    messages=messages,
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=self.model_config['temperature'],
                    max_tokens=self.model_config['max_tokens']
                )
                
                # Get completion
                completion = self.openrouter.get_completion(response)
            except Exception as api_error:
                print(f"\nAPI Error: {str(api_error)}")
                print("Generating default decision due to API error")
                return self.create_default_decision()
            
            # Skip JSON cleaning if it's already a valid JSON string
            try:
                decision_data = json.loads(completion)
                print("\nResponse was already valid JSON")
                if self.validate_decision(decision_data):
                    return decision_data
            except json.JSONDecodeError:
                # If not valid JSON, proceed with cleaning
                cleaned_json = self.clean_json_response(completion)
            
            # Try parsing with multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    print(f"\nAttempt {attempt+1}/{max_attempts} to parse decision JSON...")
                    decision_data = json.loads(cleaned_json)
                    
                    # Validate the decision data
                    if not self.validate_decision(decision_data):
                        print("\nInvalid decision format, attempting to fix structure...")
                        decision_data = self.fix_decision_structure(decision_data)
                        
                        if not self.validate_decision(decision_data):
                            if attempt == max_attempts - 1:
                                print("\nAll validation attempts failed, using default decision")
                                return self.create_default_decision()
                        else:
                            return decision_data
                    else:
                        return decision_data
                
                except json.JSONDecodeError as e:
                    print(f"\nJSON parse error on attempt {attempt+1}: {str(e)}")
                    if attempt == max_attempts - 1:
                        print("\nAll parsing attempts failed, using default decision")
                        return self.create_default_decision()
                    
                    # Try more aggressive cleaning for the next attempt
                    if "Expecting ',' delimiter" in str(e):
                        cleaned_json = self.fix_decision_delimiter_error(cleaned_json)
                    elif "Unterminated string" in str(e):
                        match = re.search(r'line (\d+) column (\d+)', str(e))
                        if match:
                            line_no, col_no = int(match.group(1)), int(match.group(2))
                            lines = cleaned_json.split('\n')
                            if line_no <= len(lines):
                                problem_line = lines[line_no - 1]
                                lines[line_no - 1] = problem_line[:col_no] + '"' + problem_line[col_no:]
                                cleaned_json = '\n'.join(lines)
                    else:
                        cleaned_json = self.fix_json_at_error(cleaned_json, str(e))
            
            # If we reach here, all attempts failed
            return self.create_default_decision()
            
        except Exception as e:
            print(f"\nError generating decision: {str(e)}")
            return self.create_default_decision()

    def fix_decision_structure(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Try to fix an invalid decision structure"""
        default = self.create_default_decision()
        
        try:
            # Copy valid parts from the original decision
            if "decision" in decision and isinstance(decision["decision"], dict):
                decision_section = decision["decision"]
                
                if "status" in decision_section and decision_section["status"] in ["PROCEED", "HOLD", "REJECT"]:
                    default["decision"]["status"] = decision_section["status"]
                
                if "confidence_score" in decision_section and isinstance(decision_section["confidence_score"], (int, float)):
                    default["decision"]["confidence_score"] = decision_section["confidence_score"]
                
                if "interview_stage" in decision_section and decision_section["interview_stage"] in ["SKIP", "SCREENING", "TECHNICAL", "FULL_LOOP"]:
                    default["decision"]["interview_stage"] = decision_section["interview_stage"]
            
            # Copy other sections if they're valid
            sections = ["rationale", "recommendations", "hiring_manager_notes", "next_steps"]
            for section in sections:
                if section in decision and isinstance(decision[section], dict):
                    # Copy valid subsections
                    for key, value in decision[section].items():
                        if key in default[section]:
                            if isinstance(value, type(default[section][key])):
                                default[section][key] = value
            
            return default
            
        except Exception as e:
            print(f"\nError fixing decision structure: {str(e)}")
            return default

    def validate_decision(self, decision: Dict[str, Any]) -> bool:
        """Validate the structure of the decision data"""
        try:
            # Check main sections
            required_sections = [
                "decision",
                "rationale",
                "recommendations",
                "hiring_manager_notes",
                "next_steps"
            ]
            if not all(section in decision for section in required_sections):
                return False

            # Validate decision section
            decision_section = decision["decision"]
            if not all(key in decision_section for key in ["status", "confidence_score", "interview_stage"]):
                return False

            # Validate status
            valid_statuses = ["PROCEED", "HOLD", "REJECT"]
            if decision_section["status"] not in valid_statuses:
                return False

            # Validate confidence score
            if not isinstance(decision_section["confidence_score"], (int, float)) or \
               not 0 <= decision_section["confidence_score"] <= 100:
                return False

            # Validate interview stage
            valid_stages = ["SKIP", "SCREENING", "TECHNICAL", "FULL_LOOP"]
            if decision_section["interview_stage"] not in valid_stages:
                return False

            # Validate rationale
            rationale = decision["rationale"]
            if not all(key in rationale for key in ["key_strengths", "concerns", "risk_factors"]):
                return False
            if not all(isinstance(rationale[key], list) for key in ["key_strengths", "concerns", "risk_factors"]):
                return False

            # Validate recommendations
            recommendations = decision["recommendations"]
            if not all(key in recommendations for key in ["interview_focus", "skill_verification", "discussion_points"]):
                return False
            if not all(isinstance(recommendations[key], list) for key in ["interview_focus", "skill_verification", "discussion_points"]):
                return False

            # Validate hiring manager notes
            manager_notes = decision["hiring_manager_notes"]
            if not all(key in manager_notes for key in ["salary_band_fit", "growth_trajectory", "team_fit_considerations", "onboarding_requirements"]):
                return False
            if not isinstance(manager_notes["onboarding_requirements"], list):
                return False

            # Validate next steps
            next_steps = decision["next_steps"]
            if not all(key in next_steps for key in ["immediate_actions", "required_approvals", "timeline_recommendation"]):
                return False
            if not isinstance(next_steps["immediate_actions"], list) or not isinstance(next_steps["required_approvals"], list):
                return False

            return True
            
        except Exception:
            return False