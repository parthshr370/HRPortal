# streamlit_app.py

import streamlit as st
import asyncio
import json
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

    async def process_markdown(self, markdown_content: str):
        """Process markdown and generate assessment"""
        try:
            assessment = await st.session_state.oa_module.process_input(markdown_content)
            st.session_state.assessment = assessment
            st.session_state.responses = {}  # Reset responses
            return True
        except Exception as e:
            st.error(f"Error processing markdown: {str(e)}")
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
            st.error(f"Error evaluating responses: {str(e)}")
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

    def run(self):
        """Main app execution"""
        self.render_header()
        
        # File upload section
        uploaded_file = st.file_uploader(
            "Upload markdown file (JD + Resume)",
            type=['md', 'txt'],
            key="file_uploader"
        )
        
        if uploaded_file:
            markdown_content = uploaded_file.read().decode()
            
            if st.button("Generate Assessment"):
                with st.spinner("Generating assessment..."):
                    asyncio.run(self.process_markdown(markdown_content))
        
        # Render assessment if available
        if st.session_state.assessment:
            assessment = st.session_state.assessment
            
            st.header("Online Assessment")
            st.write(f"Candidate: {assessment.candidate_name}")
            st.write(f"Position: {assessment.job_title}")
            
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