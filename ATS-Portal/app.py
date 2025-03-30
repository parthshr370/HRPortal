import streamlit as st
import tempfile
import os
import json
from config.config import MODELS, SUPPORTED_FILE_TYPES
from utils.file_handlers import FileHandler
from utils.text_preprocessing import TextPreprocessor
from agents.resume_parsing_agent import ResumeParsingAgent
from agents.job_matching_agent import JobMatchingAgent
from agents.decision_feedback_agent import DecisionFeedbackAgent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure API keys are loaded (handle potential missing keys)
NON_REASONING_API_KEY = os.getenv("NON_REASONING_API_KEY")
REASONING_API_KEY = os.getenv("REASONING_API_KEY")

# Update MODELS dictionary with loaded keys
if NON_REASONING_API_KEY:
    MODELS['non_reasoning']['api_key'] = NON_REASONING_API_KEY
else:
    st.error("Error: NON_REASONING_API_KEY not found in .env file. Please set it.")
    # Optionally disable parts of the app that require this key
    # st.stop() # Uncomment to stop execution if key is critical

if REASONING_API_KEY:
    MODELS['reasoning']['api_key'] = REASONING_API_KEY
else:
    st.error("Error: REASONING_API_KEY not found in .env file. Please set it.")
    # Optionally disable parts of the app that require this key
    # st.stop() # Uncomment to stop execution if key is critical


# --- Streamlit App Interface ---
st.title("ATS Portal: Resume Analyzer & Job Matcher")

# File Uploaders
st.header("Upload Files")
resume_file = st.file_uploader("Upload Resume", type=list(SUPPORTED_FILE_TYPES.values()))
st.markdown("---") # Separator
st.subheader("Job Description")
job_desc_file = st.file_uploader("Option 1: Upload Job Description File", type=list(SUPPORTED_FILE_TYPES.values()))
st.markdown("OR")
job_desc_text_area = st.text_area("Option 2: Paste Job Description Text Here", height=200)

# --- Processing Logic ---
def process_files(resume_file_obj, job_desc_file_obj=None, job_desc_pasted_text=None):
    """
    Processes uploaded resume and optional job description (from file or text area).
    Mirrors the logic of main_cli.py but uses Streamlit for I/O.
    """
    if not resume_file_obj:
        st.warning("Please upload a resume file.")
        return

    # Check if API keys are available before proceeding
    if not MODELS['non_reasoning'].get('api_key') or not MODELS['reasoning'].get('api_key'):
         st.error("One or more API keys are missing. Cannot proceed with analysis.")
         return

    try:
        # Initialize handlers early
        file_handler = FileHandler()
        text_preprocessor = TextPreprocessor()

        # Use temp files to work with uploaded resume data
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file_obj.name)[1]) as tmp_resume:
            tmp_resume.write(resume_file_obj.getvalue())
            resume_path = tmp_resume.name

        tmp_job_desc_path = None
        cleaned_job_desc = None

        # --- Determine Job Description Source ---
        if job_desc_file_obj:
            # Prioritize uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(job_desc_file_obj.name)[1]) as tmp_job:
                tmp_job.write(job_desc_file_obj.getvalue())
                tmp_job_desc_path = tmp_job.name
            st.info("Processing uploaded job description file.")
        elif job_desc_pasted_text:
            # Use pasted text if no file uploaded
            # Clean pasted text directly using the initialized preprocessor
            cleaned_job_desc = text_preprocessor.clean_text(job_desc_pasted_text)
            st.info("Processing pasted job description text.")
        # else: No job description provided

        # --- Resume Processing ---
        st.header("Resume Processing")

        with st.spinner("Extracting and cleaning resume text..."):
            st.subheader("1. Text Extraction & Cleaning")
            resume_text = file_handler.extract_text(resume_path)
            st.text(f"Extracted text length: {len(resume_text)}")
            with st.expander("Show Extracted Text (First 500 chars)"):
                st.text(resume_text[:500] + "...")

            cleaned_resume_text = text_preprocessor.clean_text(resume_text)
            st.text(f"Cleaned text length: {len(cleaned_resume_text)}")
            with st.expander("Show Cleaned Text (First 500 chars)"):
                st.text(cleaned_resume_text[:500] + "...")

        with st.spinner("Parsing resume structure..."):
            st.subheader("2. Resume Parsing")
            resume_parser = ResumeParsingAgent(
                api_key=MODELS['non_reasoning']['api_key'],
                model_name=MODELS['non_reasoning']['name']
            )
            parsed_resume = resume_parser.parse_resume(cleaned_resume_text)
            st.success("Resume parsed successfully!")
            with st.expander("Show Parsed Resume (JSON)"):
                st.json(parsed_resume)

        # --- Job Matching (if job description provided from either source) ---
        job_desc_available = tmp_job_desc_path or cleaned_job_desc

        if job_desc_available:
            st.header("Job Description Matching")
            with st.spinner("Processing job description and analyzing match..."):
                st.subheader("3. Job Description Processing")

                # Extract and clean text *only if* a file was uploaded
                # If text was pasted, cleaned_job_desc is already populated
                if tmp_job_desc_path:
                    job_desc_text = file_handler.extract_text(tmp_job_desc_path)
                    cleaned_job_desc = text_preprocessor.clean_text(job_desc_text) # Clean extracted text

                # Display cleaned job description (from file or text area)
                st.text(f"Cleaned job description length: {len(cleaned_job_desc)}")
                with st.expander("Show Cleaned Job Description (First 500 chars)"):
                    st.text(cleaned_job_desc[:500] + "...")

                st.subheader("4. Match Analysis")
                job_matcher = JobMatchingAgent(
                    api_key=MODELS['reasoning']['api_key'],
                    model_name=MODELS['reasoning']['name']
                )
                match_analysis = job_matcher.match_job(parsed_resume, cleaned_job_desc)
                st.success("Job match analysis complete!")
                with st.expander("Show Match Analysis (JSON)"):
                    st.json(match_analysis)

                st.subheader("5. Hiring Decision Feedback")
                decision_agent = DecisionFeedbackAgent(
                    api_key=MODELS['reasoning']['api_key'],
                    model_name=MODELS['reasoning']['name']
                )
                decision = decision_agent.generate_decision(
                    candidate_profile=parsed_resume,
                    match_analysis=match_analysis,
                    job_requirements=cleaned_job_desc
                )
                st.success("Hiring decision generated!")

                # Display Decision Summary (formatted like main_cli.py)
                st.text(f"Status: {decision['decision']['status']}")
                st.text(f"Confidence Score: {decision['decision']['confidence_score']}%")
                st.text(f"Recommended Interview Stage: {decision['decision']['interview_stage']}")

                st.markdown("**Key Strengths:**")
                for strength in decision['rationale']['key_strengths']:
                    st.markdown(f"- {strength}")

                st.markdown("**Areas of Concern:**")
                for concern in decision['rationale']['concerns']:
                    st.markdown(f"- {concern}")

                st.markdown("**Next Steps:**")
                for action in decision['next_steps']['immediate_actions']:
                    st.markdown(f"- {action}")

                with st.expander("Show Full Decision Feedback (JSON)"):
                    st.json(decision)

    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")
        # Consider adding more detailed error logging or traceback for debugging
        # import traceback
        # st.code(traceback.format_exc())

    finally:
        # Clean up temporary files
        if 'resume_path' in locals() and os.path.exists(resume_path):
            os.unlink(resume_path)
        if tmp_job_desc_path and os.path.exists(tmp_job_desc_path):
            os.unlink(tmp_job_desc_path)


# Trigger processing when resume is uploaded
if resume_file:
    # Pass both job description sources (file object and text area value) to the processing function
    process_files(resume_file, job_desc_file, job_desc_text_area)
else:
    st.info("Upload a resume to begin analysis. Optionally, upload or paste a job description for matching.")

# Add instructions or footer
st.sidebar.header("About")
st.sidebar.info("This app uses AI agents to parse resumes, match them against job descriptions, and provide hiring recommendations.")
st.sidebar.info("Ensure your `.env` file has `NON_REASONING_API_KEY` and `REASONING_API_KEY` set.") 