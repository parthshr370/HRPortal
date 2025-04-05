# streamlit_app.py

import streamlit as st
import asyncio
import json
import traceback
from main import OAModule
from models.data_models import Assessment, AssessmentResult

class StreamlitApp:
    def __init__(self):
        """Initialize Streamlit app with OA module"""
        # Initialize session state
        if 'oa_module' not in st.session_state:
            st.session_state.oa_module = OAModule()
        if 'assessment' not in st.session_state:
            st.session_state.assessment = None
        if 'responses' not in st.session_state:
            st.session_state.responses = {}
        if 'result' not in st.session_state:
            st.session_state.result = None
        if 'parsing_error' not in st.session_state:
            st.session_state.parsing_error = None

    async def process_markdown(self, markdown_content: str):
        """Process markdown and generate assessment"""
        try:
            # Reset any previous errors
            st.session_state.parsing_error = None
            
            # Process the markdown
            assessment = await st.session_state.oa_module.process_input(markdown_content)
            st.session_state.assessment = assessment
            st.session_state.responses = {}  # Reset responses
            return True
        except Exception as e:
            stack_trace = traceback.format_exc()
            error_message = f"Error processing markdown: {str(e)}\n{stack_trace}"
            st.session_state.parsing_error = error_message
            print(error_message)
            return False

    def render_question(self, question, question_type: str):
        """Render a single question with response input"""
        st.subheader(f"{question_type} Question")
        st.write(question.text)
        
        if question_type == "Coding":
            # Multiple choice for coding questions
            options = question.options
            response = st.radio(
                f"Select answer for Question {question.id}",
                options,
                key=f"radio_{question.id}"
            )
            st.session_state.responses[question.id] = options.index(response)
            
        elif question_type == "System Design":
            # Text area for system design questions
            st.write("Scenario:", question.scenario)
            st.write("Expected Components:", ", ".join(question.expected_components))
            response = st.text_area(
                "Your solution",
                key=f"design_{question.id}",
                height=200
            )
            st.session_state.responses[question.id] = response
            
        else:  # Behavioral
            # Text area for behavioral questions
            st.write("Context:", question.context)
            response = st.text_area(
                "Your response",
                key=f"behavioral_{question.id}",
                height=150
            )
            st.session_state.responses[question.id] = response

    async def evaluate_responses(self):
        """Evaluate all responses"""
        try:
            result = await st.session_state.oa_module.evaluate_responses(
                st.session_state.assessment,
                st.session_state.responses
            )
            st.session_state.result = result
            return True
        except Exception as e:
            stack_trace = traceback.format_exc()
            error_message = f"Error evaluating responses: {str(e)}\n{stack_trace}"
            st.error(error_message)
            print(error_message)
            return False

    def render_results(self):
        """Render assessment results"""
        result = st.session_state.result
        
        st.title("Assessment Results")
        
        # Overall score
        st.header("Overall Score")
        score_color = "green" if result.passed else "red"
        st.markdown(f"<h2 style='color: {score_color}'>{result.score}/100</h2>", unsafe_allow_html=True)
        st.write(f"Status: {'PASSED' if result.passed else 'FAILED'}")
        
        # Ratings
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Technical Rating", f"{result.technical_rating:.2f}/1.0")
        with col2:
            st.metric("Passion Rating", f"{result.passion_rating:.2f}/1.0")
        
        # Detailed feedback
        st.header("Detailed Feedback")
        for question_id, feedback in result.feedback.items():
            score = result.question_scores[question_id]
            st.subheader(f"Question {question_id}")
            st.write(f"Score: {score}/100")
            st.write(feedback)
            st.markdown("---")

    def render_header(self):
        """Render the header of the app"""
        st.title("HR Portal - Online Assessment")
        st.write("Welcome to the online assessment platform. Please upload your markdown file to proceed.")

    def render_parsed_data_preview(self, markdown_content):
        """Show a preview of the parsed data"""
        with st.expander("Preview Parsed Data", expanded=False):
            try:
                # Call parser directly to show parsed structure
                parser = st.session_state.oa_module.parser
                parsed_data = parser.parse_markdown(markdown_content)
                
                # Show job description
                st.subheader("Job Description")
                job_desc = parsed_data["job_description"]
                st.write(f"Title: {job_desc.job_title}")
                st.write(f"Location: {job_desc.location}")
                st.write(f"Experience Level: {job_desc.experience_level}")
                
                with st.expander("Responsibilities"):
                    for idx, resp in enumerate(job_desc.responsibilities, 1):
                        st.write(f"{idx}. {resp}")
                
                with st.expander("Qualifications"):
                    for idx, qual in enumerate(job_desc.qualifications, 1):
                        st.write(f"{idx}. {qual}")
                
                # Show resume
                st.subheader("Resume")
                resume = parsed_data["resume_data"]
                st.write(f"Candidate: {resume.personal_info.get('name', 'Unknown')}")
                
                with st.expander("Skills"):
                    for idx, skill in enumerate(resume.skills, 1):
                        st.write(f"{idx}. {skill}")
                
                with st.expander("Experience"):
                    for idx, exp in enumerate(resume.experience, 1):
                        st.write(f"{idx}. {exp.get('title', '')} at {exp.get('company', '')}")
                        st.write(f"   Duration: {exp.get('duration', 'Not specified')}")
                
                # Show matches
                matches = parser.extract_key_matches(parsed_data)
                st.subheader("Key Matches")
                
                with st.expander("Matched Skills"):
                    for idx, skill in enumerate(matches["skills"], 1):
                        st.write(f"{idx}. {skill}")
                
                # Candidate level
                level = parser.get_candidate_level(parsed_data)
                st.write(f"Candidate Level: {level.upper()}")
                
            except Exception as e:
                st.error(f"Error previewing parsed data: {str(e)}")

    def run(self):
        """Main app execution"""
        self.render_header()
        
        # File upload section
        uploaded_file = st.file_uploader(
            "Upload markdown file (JD + Resume)",
            type=['md', 'txt'],
            key="file_uploader"
        )
        
        # Text input alternative
        use_text_input = st.checkbox("Or enter markdown content directly")
        markdown_content = ""
        
        if use_text_input:
            markdown_content = st.text_area(
                "Enter markdown content",
                height=300,
                key="markdown_input"
            )
        elif uploaded_file:
            markdown_content = uploaded_file.read().decode()
        
        # Preview section
        if markdown_content:
            with st.expander("Preview Raw Markdown", expanded=False):
                st.text(markdown_content)
            
            if st.button("Preview Parsed Data"):
                self.render_parsed_data_preview(markdown_content)
            
            if st.button("Generate Assessment"):
                with st.spinner("Generating assessment..."):
                    success = asyncio.run(self.process_markdown(markdown_content))
                    
                    if not success and st.session_state.parsing_error:
                        st.error("Failed to generate assessment")
                        with st.expander("Error Details"):
                            st.code(st.session_state.parsing_error)
        
        # Render assessment if available
        if st.session_state.assessment:
            assessment = st.session_state.assessment
            
            st.header("Online Assessment")
            st.write(f"Candidate: {assessment.candidate_name}")
            st.write(f"Position: {assessment.job_title}")
            
            # Add download button for assessment
            assessment_json = json.dumps(assessment.dict(), indent=2)
            st.download_button(
                "Download Assessment JSON",
                assessment_json,
                "assessment.json",
                "application/json"
            )
            
            # Questions sections
            with st.expander("Coding Questions", expanded=True):
                for q in assessment.coding_questions:
                    self.render_question(q, "Coding")
                    
            with st.expander("System Design Questions", expanded=True):
                for q in assessment.system_design_questions:
                    self.render_question(q, "System Design")
                    
            with st.expander("Behavioral Questions", expanded=True):
                for q in assessment.behavioral_questions:
                    self.render_question(q, "Behavioral")
            
            # Submit button
            if st.button("Submit Assessment"):
                with st.spinner("Evaluating responses..."):
                    if asyncio.run(self.evaluate_responses()):
                        self.render_results()
                        
                        # Add download button for results
                        if st.session_state.result:
                            result_json = json.dumps(st.session_state.result.dict(), indent=2)
                            st.download_button(
                                "Download Results JSON",
                                result_json,
                                "assessment_results.json",
                                "application/json"
                            )

def main():
    st.set_page_config(
        page_title="HR Portal - Online Assessment",
        page_icon="📝",
        layout="wide"
    )
    
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()