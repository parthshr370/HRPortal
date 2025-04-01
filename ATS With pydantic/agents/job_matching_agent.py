import json
from typing import Dict, Any, List
from config.openrouter_config import OpenRouterConfig
import re
from models.resume_models import ParsedResume
from models.job_match_models import MatchAnalysis, AnalysisBreakdown
from pydantic import ValidationError

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
        
        cleaned_text = ""
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
                # Attempt to fix unterminated strings here, where 'e' is defined
                if "Unterminated string" in str(e):
                    match = re.search(r'line (\d+) column (\d+)', str(e))
                    if match:
                        line_no, col_no = int(match.group(1)), int(match.group(2))
                        # Use the 'cleaned_text' variable which holds the result of fix_json_string
                        lines = cleaned_text.split('\n') 
                        if 0 < line_no <= len(lines):
                            problem_line = lines[line_no - 1]
                            # Check bounds before slicing/inserting
                            if col_no > 0 and col_no <= len(problem_line) + 1: 
                                # Add closing quote cautiously
                                lines[line_no - 1] = problem_line[:col_no - 1] + '"' + problem_line[col_no - 1:]
                                cleaned_text = '\n'.join(lines)
                                print("\nAttempted fix for unterminated string.")
                            else:
                                print(f"\nWarning: Unterminated string error at invalid position ({line_no}, {col_no}).")
                        else:
                            print(f"\nWarning: Unterminated string error reported for invalid line number {line_no}." )
                    else:
                         print("\nWarning: Could not parse line/column for Unterminated string error.")

            
            # Second attempt: More aggressive cleaning (using potentially fixed cleaned_text)
            print("\nCleaned text (before second attempt):")
            print(cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text)
            
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text) # Use potentially fixed text
            cleaned_text = re.sub(r'{(\s+)?}', '{}', cleaned_text)
            cleaned_text = re.sub(r'\[(\s+)?\]', '[]', cleaned_text)
            
            print("\nCleaned text (second attempt):")
            print(cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text)
            
            # Validate JSON after second attempt
            try:
                json.loads(cleaned_text)
                return cleaned_text
            except json.JSONDecodeError:
                print("\nSecond cleaning attempt failed.")
                # Third attempt: Extract just the JSON portion from the ORIGINAL response
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
                        return json.dumps(self.create_default_analysis().dict())
                else:
                    return json.dumps(self.create_default_analysis().dict())
            
        except Exception as e:
            print(f"\nError in JSON cleaning: {str(e)}")
            # If all else fails, return a valid default structure
            return json.dumps(self.create_default_analysis().dict())

    def create_default_analysis(self) -> MatchAnalysis:
        """Create a default analysis structure using Pydantic model"""
        empty_breakdown = AnalysisBreakdown(
            score=0.0,
            details=["Analysis failed - please try again"]
        )
        
        return MatchAnalysis(
            overall_match_score=0.0,
            skills_match=empty_breakdown,
            experience_match=empty_breakdown,
            education_match=empty_breakdown,
            additional_insights=["Analysis failed - please try again"]
        )

    def _transform_api_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API response to match Pydantic model structure"""
        try:
            print("\nTransforming raw API response data:")
            print(f"Raw match_score: {raw_data.get('match_score', 0)}")
            
            # Extract scores and convert from 0-100 to 0.0-1.0
            match_score = raw_data.get("match_score", 0) / 100.0
            
            # Extract analysis sections with safe defaults
            analysis = raw_data.get("analysis", {})
            skills = analysis.get("skills", {})
            experience = analysis.get("experience", {})
            education = analysis.get("education", {})
            additional = analysis.get("additional", {})
            
            # Debug logging
            print(f"Skills score: {skills.get('score', 0)}")
            print(f"Experience score: {experience.get('score', 0)}")
            print(f"Education score: {education.get('score', 0)}")
            
            # Create transformed data structure
            transformed_data = {
                "overall_match_score": match_score,
                "skills_match": {
                    "score": skills.get("score", 0) / 100.0,
                    "details": self._combine_matches_gaps(
                        skills.get("matches", []),
                        skills.get("gaps", [])
                    )
                },
                "experience_match": {
                    "score": experience.get("score", 0) / 100.0,
                    "details": self._combine_matches_gaps(
                        experience.get("matches", []),
                        experience.get("gaps", [])
                    )
                },
                "education_match": {
                    "score": education.get("score", 0) / 100.0,
                    "details": self._combine_matches_gaps(
                        education.get("matches", []),
                        education.get("gaps", [])
                    )
                },
                "additional_insights": []
            }
            
            # Add additional insights
            recommendation = raw_data.get("recommendation", "")
            if recommendation:
                transformed_data["additional_insights"] = [recommendation]
            
            # Add strengths and considerations
            strengths = raw_data.get("key_strengths", [])
            considerations = raw_data.get("areas_for_consideration", [])
            
            if strengths:
                transformed_data["additional_insights"].append("Key Strengths:")
                transformed_data["additional_insights"].extend([f"+ {strength}" for strength in strengths])
            
            if considerations:
                transformed_data["additional_insights"].append("Areas for Consideration:")
                transformed_data["additional_insights"].extend([f"- {area}" for area in considerations])
            
            # Ensure we have at least one additional insight
            if not transformed_data["additional_insights"]:
                transformed_data["additional_insights"] = ["No additional insights available"]
            
            print("\nTransformed data:")
            print(f"overall_match_score: {transformed_data['overall_match_score']}")
            print(f"skills_match.score: {transformed_data['skills_match']['score']}")
            print(f"experience_match.score: {transformed_data['experience_match']['score']}")
            print(f"education_match.score: {transformed_data['education_match']['score']}")
            
            return transformed_data
        
        except Exception as e:
            print(f"Error transforming API response: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return a minimal valid structure on error
            return {
                "overall_match_score": 0.0,
                "skills_match": {"score": 0.0, "details": ["Error transforming API response"]},
                "experience_match": {"score": 0.0, "details": ["Error transforming API response"]},
                "education_match": {"score": 0.0, "details": ["Error transforming API response"]},
                "additional_insights": ["Error occurred while transforming the analysis results"]
            }

    def _combine_matches_gaps(self, matches: List[str], gaps: List[str]) -> List[str]:
        """Combine matches and gaps into a single list of details"""
        result = []
        if matches:
            result.append("Matches:")
            result.extend([f"+ {match}" for match in matches])
        if gaps:
            result.append("Gaps:")
            result.extend([f"- {gap}" for gap in gaps])
        return result if result else ["No specific details available"]

    def match_job(self, candidate_profile: ParsedResume, job_description: str) -> MatchAnalysis:
        """Compare candidate profile against job description and return match analysis"""
        try:
            # Format the input content
            formatted_content = (
                f"Candidate Profile:\n{json.dumps(candidate_profile.dict(), indent=2)}\n\n"
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
            
            # Parse and validate the response with Pydantic
            try:
                # Attempt to load the cleaned JSON into a dictionary first
                raw_analysis_data = json.loads(cleaned_json)
                print("\nRaw API data structure:")
                print(json.dumps(raw_analysis_data, indent=2)[:500] + "..." if len(json.dumps(raw_analysis_data, indent=2)) > 500 else json.dumps(raw_analysis_data, indent=2))
                
                # Transform the data to match the Pydantic model structure
                transformed_data = self._transform_api_response(raw_analysis_data)
                print("\nAfter transformation:")
                print(json.dumps(transformed_data, indent=2)[:500] + "..." if len(json.dumps(transformed_data, indent=2)) > 500 else json.dumps(transformed_data, indent=2))
                
                # Now parse and validate using Pydantic
                match_analysis = MatchAnalysis(**transformed_data)
                print("\nFinal Pydantic model:")
                print(json.dumps(match_analysis.dict(), indent=2)[:500] + "..." if len(json.dumps(match_analysis.dict(), indent=2)) > 500 else json.dumps(match_analysis.dict(), indent=2))
                
                return match_analysis

            except json.JSONDecodeError as json_err:
                print(f"\nJSON decode error during job matching: {json_err}")
                # Log the problematic JSON: print(f"Problematic JSON: {cleaned_json}")
                return self.create_default_analysis() # Return default on JSON error

            except ValidationError as ve:
                print(f"\nPydantic validation error during job matching: {ve}")
                # Log the raw data and validation errors: print(f"Raw data: {raw_analysis_data}", ve.json())
                # Attempt to fix might be complex, return default for now
                # Or potentially try self.fix_analysis_structure(raw_analysis_data) if adapted
                return self.create_default_analysis() # Return default on validation error

        except Exception as e:
            print(f"\nError in job matching: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_default_analysis()