import json
from typing import Dict, Any
from config.openrouter_config import OpenRouterConfig
import re
from models.resume_models import ParsedResume
from models.job_match_models import MatchAnalysis
from models.decision_models import DecisionFeedback
from pydantic import ValidationError

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
        except json.JSONDecodeError as e2:
            print(f"\nBasic cleaning failed: {str(e2)}. Attempting structural fixes...")
            
            # 3. Apply structural fixes based on the error *e2*
            
            # Handle unterminated strings (based on e2)
            if "Unterminated string" in str(e2):
                match = re.search(r'line (\d+) column (\d+)', str(e2))
                if match:
                    line_no, col_no = int(match.group(1)), int(match.group(2))
                    lines = cleaned_text.split('\n')
                    if 0 < line_no <= len(lines):
                        problem_line = lines[line_no - 1]
                        # Ensure col_no is within valid range before slicing
                        if 0 < col_no <= len(problem_line) + 1:
                            # Add closing quote cautiously
                            lines[line_no - 1] = problem_line[:col_no - 1] + '"' + problem_line[col_no - 1:]
                            cleaned_text = '\n'.join(lines)
                            print("\nAttempted fix for unterminated string.")
            
            # Handle missing commas (based on e2)
            if "Expecting ',' delimiter" in str(e2):
                match = re.search(r'line (\d+) column (\d+)', str(e2))
                if match:
                    line_no, col_no = int(match.group(1)), int(match.group(2))
                    lines = cleaned_text.split('\n')
                    if 0 < line_no <= len(lines):
                        problem_line = lines[line_no - 1]
                        # Ensure col_no is within valid range
                        if 0 < col_no <= len(problem_line) + 1:
                            # Try to insert a comma at the problematic position
                            lines[line_no - 1] = problem_line[:col_no - 1] + ',' + problem_line[col_no - 1:]
                            cleaned_text = '\n'.join(lines)
                            print("\nAttempted fix for missing comma.")
        
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

    def create_default_decision(self) -> DecisionFeedback:
        """Create a default decision structure using Pydantic model"""
        # Use the Pydantic model's default factory
        return DecisionFeedback(
             rationale=dict(
                 key_strengths=["Unable to determine due to processing error"],
                 concerns=["Unable to process candidate data completely"],
                 risk_factors=["Decision based on incomplete information"]
             ),
             recommendations=dict(
                 interview_focus=["Verify resume contents manually"],
                 skill_verification=["Conduct thorough technical assessment"],
                 discussion_points=["Discuss areas mentioned in resume"]
             ),
             hiring_manager_notes=dict(
                 salary_band_fit="Unable to determine",
                 growth_trajectory="Unable to determine",
                 team_fit_considerations="Manual assessment required",
                 onboarding_requirements=["Standard onboarding process"]
             ),
             next_steps=dict(
                 immediate_actions=["Re-run analysis or manually review"],
                 required_approvals=["Hiring manager approval needed"],
                 timeline_recommendation="Proceed with caution due to data processing issues"
             )
        )

    def generate_decision(
        self,
        candidate_profile: ParsedResume,
        match_analysis: MatchAnalysis,
        job_requirements: str
    ) -> DecisionFeedback:
        """Generate a comprehensive hiring decision using Pydantic models"""
        try:
            # Format input data using .dict() for Pydantic models
            formatted_content = (
                f"Candidate Profile:\\n{json.dumps(candidate_profile.dict(), indent=2)}\\n\\n"
                f"Match Analysis:\\n{json.dumps(match_analysis.dict(), indent=2)}\\n\\n"
                f"Job Requirements:\\n{job_requirements}"
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
                raw_decision_data = json.loads(completion)
                print("\nResponse might be valid JSON already, attempting Pydantic parse...")
                # Directly try to parse with Pydantic
                decision_data = DecisionFeedback(**raw_decision_data)
                print("\nSuccessfully parsed existing JSON with Pydantic.")
                return decision_data
            except (json.JSONDecodeError, ValidationError) as initial_parse_error:
                print(f"\nInitial parse failed ({type(initial_parse_error).__name__}), proceeding with cleaning...")
                # If not valid JSON or doesn't match Pydantic model, proceed with cleaning
                cleaned_json = self.clean_json_response(completion)
            
            # Try parsing the *cleaned* JSON with Pydantic
            try:
                print("\nAttempting to parse cleaned decision JSON with Pydantic...")
                raw_decision_data = json.loads(cleaned_json)
                decision_data = DecisionFeedback(**raw_decision_data)
                print("\nSuccessfully parsed cleaned JSON with Pydantic.")
                return decision_data
            
            except json.JSONDecodeError as json_err:
                print(f"\nJSON parse error after cleaning: {json_err}")
                print(f"Cleaned JSON that failed: {cleaned_json[:500]}...")
                return self.create_default_decision()
            
            except ValidationError as ve:
                print(f"\nPydantic validation error after cleaning: {ve}")
                return self.create_default_decision()
            
        except Exception as e:
            print(f"\nError generating decision: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_default_decision()